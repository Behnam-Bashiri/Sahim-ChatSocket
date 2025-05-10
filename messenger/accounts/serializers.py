from rest_framework import serializers
from .models import UserProfile, PhoneOTP


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "profile_picture",
            "email_verified",
            "phone_number_verified",
        ]


class PhoneOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneOTP
        fields = ["phone_number", "otp_code", "created_at", "is_verified"]
