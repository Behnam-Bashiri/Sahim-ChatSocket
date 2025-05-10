from .repositories import UserProfileRepository, PhoneOTPRepository
from .models import PhoneOTP
from django.core.exceptions import ValidationError


class AuthService:
    @staticmethod
    def register_or_get_user(phone_number, otp_code=None):
        user, created = UserProfileRepository.create_or_get_user(phone_number)

        if not user:
            raise ValidationError("User could not be created")

        if otp_code and not AuthService.verify_otp(phone_number, otp_code):
            raise ValidationError("Invalid OTP code")

        return user, created

    @staticmethod
    def create_otp(phone_number):
        otp_code = "123456"
        otp = PhoneOTPRepository.create_otp(phone_number, otp_code)
        return otp

    @staticmethod
    def verify_otp(phone_number, otp_code):
        otp = PhoneOTPRepository.get_otp(phone_number, otp_code)
        if otp and not otp.is_expired():
            return True
        return False
