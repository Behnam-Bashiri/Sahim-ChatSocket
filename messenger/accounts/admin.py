from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, PhoneOTP
from modern_django_admin.admin import modern_admin_site


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


modern_admin_site.register(UserProfile, UserProfileAdmin)
modern_admin_site.register(PhoneOTP, PhoneOTPAdmin)
