# accounts/repositories.py
from .models import UserProfile, PhoneOTP
from django.db import IntegrityError


class UserProfileRepository:
    @staticmethod
    def create_or_get_user(phone_number):
        try:
            user, created = UserProfile.objects.get_or_create(phone_number=phone_number)
            return user, created
        except IntegrityError:
            return None, False

    @staticmethod
    def get_user_by_phone(phone_number):
        return UserProfile.objects.filter(phone_number=phone_number).first()


class PhoneOTPRepository:
    @staticmethod
    def get_otp(phone_number, otp_code):
        return PhoneOTP.objects.filter(
            phone_number=phone_number, otp_code=otp_code
        ).first()

    @staticmethod
    def create_otp(phone_number, otp_code):
        otp = PhoneOTP(phone_number=phone_number, otp_code=otp_code)
        otp.save()
        return otp
