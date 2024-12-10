from django import forms
from .models import UserData
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


UserData = get_user_model()

class UserDataForm(UserCreationForm):
    class Meta:
        model = UserData
        fields = ['first_name', 'last_name', 'email', 'password']