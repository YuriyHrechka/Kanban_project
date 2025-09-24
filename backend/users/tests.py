from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class AuthFlowTests(TestCase):
    """
    Tests for the user authentication flow: registration, token obtain, and token refresh.
    """

    def setUp(self):
        """
        Initialize APIClient and endpoint URLs used in tests.
        """
        self.client = APIClient()
        self.register_url = reverse("auth_register")
        self.token_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")

    def test_register_creates_user_and_returns_tokens(self):
        """
        Ensure registering a user returns access and refresh tokens and creates the user.
        """
        payload = {"username": "tester", "password": "StrongP@ssw0rd"}
        resp = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

    def test_token_obtain_with_valid_credentials(self):
        """
        Verify token obtain endpoint returns access and refresh tokens for valid credentials.
        """
        user = User.objects.create_user(username="loginuser", password="P@ssw0rd123")
        resp = self.client.post(
            self.token_url,
            {"username": "loginuser", "password": "P@ssw0rd123"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

    def test_token_obtain_with_invalid_credentials(self):
        """
        Ensure token obtain fails with HTTP 401 for invalid credentials.
        """
        resp = self.client.post(
            self.token_url, {"username": "noone", "password": "bad"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_rotates_and_blacklists_previous(self):
        """
        Test token refresh behavior: refresh succeeds and, if rotation is enabled, the old refresh is rejected.
        """
        user = User.objects.create_user(username="refuser", password="P@ssw0rd123")
        refresh = RefreshToken.for_user(user)
        old_refresh = str(refresh)

        resp = self.client.post(self.refresh_url, {"refresh": old_refresh}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)

        new_refresh = resp.data.get("refresh")
        if new_refresh:
            resp2 = self.client.post(self.refresh_url, {"refresh": old_refresh}, format="json")
            # Depending on SimpleJWT settings, old refresh may be rejected with 401 or 400
            self.assertIn(
                resp2.status_code,
                (status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST),
            )

    def test_register_confirm_password_mismatch(self):
        """
        Register should fail when `confirm_password` does not match `password`.
        """
        payload = {
            "username": "mismatch",
            "password": "StrongP@ssw0rd",
            "confirm_password": "different",
        }
        resp = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("confirm_password", resp.data)

    def test_profile_endpoint_requires_auth_and_returns_user(self):
        """
        Ensure profile endpoint requires authentication and returns the authenticated user's profile.
        """
        profile_url = reverse("user_profile")
        resp = self.client.get(profile_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        payload = {"username": "proftest", "password": "StrongP@ssw0rd"}
        reg = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(reg.status_code, status.HTTP_201_CREATED)
        access = reg.data.get("access")
        self.assertIsNotNone(access)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        resp2 = self.client.get(profile_url)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp2.data.get("username"), "proftest")
