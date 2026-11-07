from django.test import TestCase
from django.contrib.auth.models import (
    User,
    Group,
    Permission,
)
from hashlib import sha1  # Used to securely hash data (like tokens)
from .models import ResetToken


class UserModelTest(TestCase):
    def setUp(self):
        # Create a User object for testing
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_user_has_username(self):
        # Test that a User object has the expected username
        self.assertEqual(self.user.username, "testuser")

    def test_user_has_password(self):
        # Test that a User object has the expected password
        self.assertTrue(self.user.check_password("testpassword"))


class ResetTokenModelTest(TestCase):
    def setUp(self):
        # Create a User object for testing
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        # Create a ResetToken object for testing
        self.reset_token = ResetToken.objects.create(
            user=self.user,
            token="testtoken",
            expiry_date="2024-12-31 23:59:59",
            used=False,
        )

    def test_reset_token_has_user(self):
        # Test that a ResetToken object has the expected user
        self.assertEqual(self.reset_token.user, self.user)

    def test_reset_token_has_token(self):
        # Test that a ResetToken object has the expected token
        self.assertEqual(self.reset_token.token, "testtoken")

    def test_reset_token_has_expiry_date(self):
        # Test that a ResetToken object has the expected expiry date
        self.assertEqual(
            str(self.reset_token.expiry_date), "2024-12-31 23:59:59"
        )

    def test_reset_token_has_used_flag(self):
        # Test that a ResetToken object has the expected used flag
        self.assertFalse(self.reset_token.used)
