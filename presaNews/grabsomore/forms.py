from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm

from .models import Journalist, Reader


class CustomUserCreationForm(AdminUserCreationForm):

    class Meta:
        model = Journalist
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = Journalist
        fields = ("username", "email")
