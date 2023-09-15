from django.forms import ModelForm
from .models import UserProxy
from django import forms
from uuid import uuid4


def email_unique(value):
    if UserProxy.objects.filter(email=value).first():
        raise forms.ValidationError("That email already exists.")


class UserProxyForm(ModelForm):
    username = forms.CharField(max_length=255, required=False, empty_value=str(uuid4()))
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True, validators=[email_unique])

    class Meta:
        model = UserProxy
        fields = ["username", "first_name", "last_name", "email"]
