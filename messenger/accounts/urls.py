from django.urls import path
from .views import RegisterOrCreateOTPView, UserProfileView, VerifyOTPView, UserListView

urlpatterns = [
    path(
        "register-or-create-otp/",
        RegisterOrCreateOTPView.as_view(),
        name="register_or_create_otp",
    ),
    path(
        "verify-otp/",
        VerifyOTPView.as_view(),
        name="verify-otp",
    ),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("users/", UserListView.as_view(), name="user_list"),
]
