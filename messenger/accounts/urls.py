from django.urls import path
from .views import RegisterOrCreateOTPView, UserProfileView

urlpatterns = [
    path(
        "register-or-create-otp/",
        RegisterOrCreateOTPView.as_view(),
        name="register_or_create_otp",
    ),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
]
