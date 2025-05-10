# accounts/tests/test_models.py
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.db import IntegrityError
from accounts.models import PhoneOTP, UserProfile


class PhoneOTPModelTest(TestCase):
    def test_is_expired(self):
        otp = PhoneOTP.objects.create(
            phone_number="1234567890",
            otp_code="123456",
            created_at=timezone.now() - timedelta(minutes=3),
        )
        self.assertTrue(otp.is_expired())

    def test_is_not_expired(self):
        otp = PhoneOTP.objects.create(
            phone_number="1234567890",
            otp_code="123456",
            created_at=timezone.now() - timedelta(minutes=1),
        )
        self.assertFalse(otp.is_expired())


class UserProfileModelTest(TestCase):
    def test_create_user_profile(self):
        user = UserProfile.objects.create(
            phone_number="1234567890",
            first_name="John",
            last_name="Doe",
            password="testpassword",
        )
        self.assertEqual(user.phone_number, "1234567890")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertTrue(user.check_password("testpassword"))

    def test_create_user_with_duplicate_phone_number(self):
        UserProfile.objects.create(
            phone_number="1234567890",
            first_name="John",
            last_name="Doe",
            password="testpassword",
        )
        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(
                phone_number="1234567890",
                first_name="Jane",
                last_name="Doe",
                password="testpassword",
            )
