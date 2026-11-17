from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from newsletter.models import Article, Publisher, Newsletter


class ResetToken(models.Model):
    # Reference to the user who requested the password reset
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    # Token string, unique to avoid duplicates
    token = models.CharField(max_length=255, unique=True)
    # When this token expires
    expiry_date = models.DateTimeField()
    # Whether this token has already been used
    used = models.BooleanField(default=False)

    def __str__(self):
        # Show a short summary for easier debugging
        return f"ResetToken(user={self.user.username}, token={self.token[:10]}..., used={self.used})"


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False)
    publisher = models.ForeignKey(
        Publisher, on_delete=models.CASCADE, null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    publisher_subscriptions = models.ManyToManyField(
        Publisher, related_name="subscriptions_publisher",
        blank=True
        )

    journalist_subscriptions = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="subscriptions_journalist",
        blank=True
        )

    def __str__(self):
        return self.username
