from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import PhoneOTP, UserProfile
from rest_framework_simplejwt.tokens import RefreshToken


class VerifyOTPViewTest(APITestCase):
    def setUp(self):
        self.phone_number = "1234567890"
        self.otp_code = "123456"
        self.user = UserProfile.objects.create(
            phone_number=self.phone_number,
            first_name="John",
            last_name="Doe",
            password="testpassword",
        )
        PhoneOTP.objects.create(
            phone_number=self.phone_number, otp_code=self.otp_code, is_verified=False
        )

    def test_verify_otp_success(self):
        response = self.client.post(
            "/api/verify-otp/",
            {"phone_number": self.phone_number, "otp_code": self.otp_code},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertEqual(response.data["detail"], "OTP verified successfully")

    def test_verify_otp_failure_invalid_code(self):
        response = self.client.post(
            "/api/verify-otp/",
            {"phone_number": self.phone_number, "otp_code": "wrongotp"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid OTP code")


class RegisterOrCreateOTPViewTest(APITestCase):
    def test_register_or_create_otp_success(self):
        response = self.client.post(
            "/api/register-or-create-otp/",
            {"phone_number": "1234567890"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("otp_code", response.data)

    def test_register_or_create_otp_failure_existing_user(self):
        UserProfile.objects.create(
            phone_number="1234567890",
            first_name="John",
            last_name="Doe",
            password="testpassword",
        )
        response = self.client.post(
            "/api/register-or-create-otp/",
            {"phone_number": "1234567890"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("otp_code", response.data)
