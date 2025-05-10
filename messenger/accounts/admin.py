from django.contrib import admin
from .models import UserProfile, PhoneOTP
from django.utils.html import format_html
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile
from django.forms import TextInput, Textarea
from django import forms


class UserProfileAdmin(UserAdmin):
    model = UserProfile
    list_display = ("phone_number", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "profile_picture")}),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    search_fields = ("phone_number",)
    ordering = ("phone_number",)


class PhoneOTPAdmin(admin.ModelAdmin):
    list_display = (
        "phone_number",
        "otp_code",
        "created_at",
        "is_verified",
        "is_expired_status",
    )
    search_fields = ("phone_number", "otp_code")
    list_filter = ("is_verified",)

    def is_expired_status(self, obj):
        return "Expired" if obj.is_expired() else "Valid"

    is_expired_status.short_description = "OTP Status"


# Registering models in admin
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(PhoneOTP, PhoneOTPAdmin)
