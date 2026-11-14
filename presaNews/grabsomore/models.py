from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


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


class Journalist(AbstractUser):
    articles = models.ForeignKey("Article", on_delete=models.CASCADE, related_name="journalist_articles")
    # The articles that the journalist has written; if an article is deleted, it is also removed from the journalist's profile

    newsletters = models.ForeignKey("Newsletter", on_delete=models.CASCADE, related_name="journalist_newsletters")
    # The newsletters that the journalist has contributed to; if a newsletter is deleted, it is also removed from the journalist's profile

    def __str__(self):
        return self.username


class Reader(AbstractUser):
    publisher_subscription = models.ManyToManyField("Publisher", related_name="subscribers_p")
    # The publishers that the user is subscribed to; if a publisher is deleted, the subscription is also deleted

    journalist_subscription = models.ManyToManyField("Journalist", related_name="subscribers_j")
    # The journalists that the user is subscribed to; if a journalist is deleted, the subscription is also deleted

    def __str__(self):
        return self.username
