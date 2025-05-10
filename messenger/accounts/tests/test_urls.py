# accounts/tests/test_urls.py
from django.urls import reverse
from rest_framework.test import APITestCase


class UserProfileURLTest(APITestCase):
    def test_user_profile_url(self):
        url = reverse("user-profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_register_or_create_otp_url(self):
        url = reverse("register-or-create-otp")
        response = self.client.post(url, {"phone_number": "1234567890"})
        self.assertEqual(response.status_code, 200)
