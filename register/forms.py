from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()

    CURRENCY_CHOICES = [
        ("GBP", "British Pound"),
        ("USD", "US Dollar"),
        ("EUR", "Euro"),
    ]

    currency = forms.ChoiceField(choices=CURRENCY_CHOICES)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "currency",
            "password1",
            "password2",
        ]

class CreateAdminForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]