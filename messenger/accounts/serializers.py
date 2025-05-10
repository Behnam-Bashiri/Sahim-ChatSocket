from rest_framework import serializers
from .models import UserProfile, PhoneOTP


class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "profile_picture",
            "profile_picture_url",
            "email_verified",
            "phone_number_verified",
        ]

    def get_profile_picture_url(self, obj):
        request = self.context.get("request")
        if obj.profile_picture and request:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None


class PhoneOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneOTP
        fields = ["phone_number", "otp_code", "created_at", "is_verified"]
