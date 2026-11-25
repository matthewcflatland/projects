from newsletter.models import Publisher
from django.contrib.auth.models import (
    Group,
    Permission,
)  # Django's built-in user, group, and permission models


def create_publisher(new_publisher, username):

    if new_publisher == "" or new_publisher == "Optional":
        publisher = None

    else:
        try:
            publisher = Publisher.objects.get(name=new_publisher)
        except Publisher.DoesNotExist:
            publisher = Publisher.objects.create(name=new_publisher)            

    return publisher


def create_reader():
    """creates the reader group if it does not exist or applies
      the reader group to the new user"""
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
    """creates the editor group if it does not exist or applies
    the editor group to the new user"""
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
            ),
            Permission.objects.get(
                codename="add_newsletter",
                content_type__app_label="newsletter"
            ),
        ])
        group.save()

    return group


def create_journalist():
    """creates the journalist group if it does not exist or applies
      the journalist group to the new user"""
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
