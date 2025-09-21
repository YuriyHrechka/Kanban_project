from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class AuthFlowTests(TestCase):
    """
    The `AuthFlowTests` class contains test methods for user authentication flow including user
    registration, token obtain with valid and invalid credentials, and token refresh functionality.
    """

    def setUp(self):
        """
        The setUp function initializes necessary variables for testing API endpoints in a Django
        project.
        """
        self.client = APIClient()
        self.register_url = reverse("auth_register")
        self.token_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")

    def test_register_creates_user_and_returns_tokens(self):
        """
        The function `test_register_creates_user_and_returns_tokens` tests user registration functionality
        by creating a user and returning access and refresh tokens.
        """
        payload = {"username": "tester", "password": "StrongP@ssw0rd"}
        resp = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)
        self.assertIn("user_id", resp.data)
        self.assertTrue(User.objects.filter(username="tester").exists())

    def test_token_obtain_with_valid_credentials(self):
        """
        The function tests token obtain with valid credentials by creating a user and making a POST request
        to obtain access and refresh tokens.
        """
        # create user
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
        This function tests token obtain with invalid credentials by sending a POST request with incorrect
        username and password.
        """
        resp = self.client.post(
            self.token_url, {"username": "noone", "password": "bad"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_rotates_and_blacklists_previous(self):
        """
        The function `test_token_refresh_rotates_and_blacklists_previous` creates a user, generates a
        refresh token, performs a refresh request, and checks the response status and data.
        """
        # create user and get refresh
        user = User.objects.create_user(username="refuser", password="P@ssw0rd123")
        refresh = RefreshToken.for_user(user)
        old_refresh = str(refresh)

        # perform refresh request
        resp = self.client.post(
            self.refresh_url, {"refresh": old_refresh}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)

        # if rotation is enabled, a new refresh may be returned
        new_refresh = resp.data.get("refresh")
        if new_refresh:
            # old refresh should be blacklisted (attempt using old refresh should fail)
            resp2 = self.client.post(
                self.refresh_url, {"refresh": old_refresh}, format="json"
            )
            # either 401 or 400 depending on SimpleJWT config
            self.assertIn(
                resp2.status_code,
                (status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST),
            )
