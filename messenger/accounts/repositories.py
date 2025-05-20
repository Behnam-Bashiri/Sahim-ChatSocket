from .models import UserProfile, PhoneOTP
from django.db import IntegrityError
from django.db.models import Q, QuerySet
from typing import Optional, Tuple, Union, Set


class UserProfileRepository:
    @staticmethod
    def create_or_get_user(phone_number: str) -> Tuple[Optional[UserProfile], bool]:
        try:
            user, created = UserProfile.objects.get_or_create(phone_number=phone_number)
            return user, created
        except IntegrityError:
            return None, False

    @staticmethod
    def get_user_by_phone(phone_number: str) -> Optional[UserProfile]:
        return UserProfile.objects.filter(phone_number=phone_number).first()

    @staticmethod
    def get_users_by_ids(user_ids: Set[int]) -> QuerySet[UserProfile]:
        return UserProfile.objects.filter(id__in=user_ids)

    @staticmethod
    def list_users(search: Optional[str] = None) -> QuerySet[UserProfile]:
        qs = UserProfile.objects.all()
        if search:
            qs = qs.filter(
                Q(phone_number__icontains=search) | Q(username__icontains=search)
            )
        return qs

    @staticmethod
    def search_users(
        phone_number: str = "",
        first_name: str = "",
        last_name: str = "",
        exclude_user_id: Optional[int] = None,
    ) -> QuerySet[UserProfile]:
        filters = Q()

        if phone_number:
            filters &= Q(phone_number__icontains=phone_number)
        if first_name:
            filters &= Q(first_name__icontains=first_name)
        if last_name:
            filters &= Q(last_name__icontains=last_name)

        queryset = UserProfile.objects.filter(filters)
        if exclude_user_id:
            queryset = queryset.exclude(id=exclude_user_id)

        return queryset


class PhoneOTPRepository:
    @staticmethod
    def get_otp(phone_number: str, otp_code: str) -> Optional[PhoneOTP]:
        return PhoneOTP.objects.filter(
            phone_number=phone_number, otp_code=otp_code
        ).first()

    @staticmethod
    def create_otp(phone_number: str, otp_code: str) -> PhoneOTP:
        otp = PhoneOTP(phone_number=phone_number, otp_code=otp_code)
        otp.save()
        return otp

    @staticmethod
    def delete_otp(phone_number: str, otp_code: str) -> bool:
        otp = PhoneOTP.objects.filter(
            phone_number=phone_number, otp_code=otp_code
        ).first()
        if otp:
            otp.delete()
            return True
        return False
