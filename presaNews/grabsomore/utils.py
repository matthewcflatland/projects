from django.core.mail import EmailMessage  # Used to create and send emails
from hashlib import sha1  # Used to securely hash data (like tokens)
from datetime import datetime, timedelta  # To handle dates and times
from .models import ResetToken  # Our model to store password reset tokens
from django.urls import reverse  # To get URL from named paths
from django.contrib.auth.models import (
    User,
    Group,
    Permission,
)  # Django's built-in user, group, and permission models


# This function creates a special reset link for the user
def generate_reset_url(user):
    # Create a unique token by hashing username + current time
    token = sha1((user.username + str(datetime.now())).encode()).hexdigest()

    # Set the token to expire in 1 hour from now
    expiry = datetime.now() + timedelta(hours=1)

    # Save this token and expiry time in the database linked to the user
    ResetToken.objects.create(user=user, token=token, expiry_date=expiry)

    # Return the URL path for the password reset page, including the token
    # This URL will be something like /grabsomore/reset_password/<token>/
    return reverse("grabsomore:password_reset_token", kwargs={"token": token})


# This function creates the email that will be sent to the user
def build_email(user, url):
    subject = "Password Reset Request"  # Email subject line

    # Email message body, showing the user their reset link
    # The URL includes the reset token, so they can reset their
    # password securely
    body = (
        f"Hello {user.username},\n\nClick the link below to"
        f" reset your password:\n\nhttp://localhost:8000{url}"
    )

    # Create the email object, setting the recipient to the user's
    # email address
    email = EmailMessage(subject, body, to=[user.email])

    return email  # Return the email object so it can be sent later


def create_reader():
    try:
        group = Group.objects.get(name="Reader")
    except Group.DoesNotExist:
        # If it doesn't exist, create it
        group = Group.objects.create(name="Reader")
        group.permissions.set([
            Permission.objects.get(
                codename="view_article",
                content_type__app_label="newsletter"
            ),
            Permission.objects.get(
                codename="view_newsletter",
                content_type__app_label="newsletter"
            )
        ])
        group.save()

    return group


def create_editor():
    try:
        group = Group.objects.get(name="Editor")
    except Group.DoesNotExist:
        # If it doesn't exist, create it
        group = Group.objects.create(name="Editor")
        group.permissions.set([
            Permission.objects.get(
                codename="view_article",
                content_type__app_label="newsletter"
            ),
            Permission.objects.get(
                codename="change_article",
                content_type__app_label="newsletter"
            ),
            Permission.objects.get(
                codename="delete_article",
                content_type__app_label="newsletter"
            ),
            Permission.objects.get(
                codename="view_newsletter",
                content_type__app_label="newsletter"
            ),
            Permission.objects.get(
                codename="change_newsletter",
                content_type__app_label="newsletter"
            ),
            Permission.objects.get(
                codename="delete_newsletter",
                content_type__app_label="newsletter"
            )
        ])
        group.save()

    return group


def create_journalist():
    try:
        group = Group.objects.get(name="Journalist")
    except Group.DoesNotExist:
        # If it doesn't exist, create it
        group = Group.objects.create(name="Journalist")
        group.permissions.set([
            Permission.objects.get(
                codename="view_article",
                content_type__app_label="newsletter"
            ),
            Permission.objects.get(
                codename="change_article",
                content_type__app_label="newsletter"
            ),
            Permission.objects.get(
                codename="delete_article",
                content_type__app_label="newsletter"
            ),
            Permission.objects.get(
                codename="add_article",
                content_type__app_label="newsletter"
            ),
            Permission.objects.get(
                codename="view_newsletter",
                content_type__app_label="newsletter"
            ),
            Permission.objects.get(
                codename="change_newsletter",
                content_type__app_label="newsletter"
            ),
            Permission.objects.get(
                codename="delete_newsletter",
                content_type__app_label="newsletter"
            ),
            Permission.objects.get(
                codename="add_newsletter",
                content_type__app_label="newsletter"
            )
        ])
        group.save()

    return group
