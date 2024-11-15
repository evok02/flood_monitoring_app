from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.conf import settings
from .form import UserDataForm


def Home(request):
    return render(request, 'index.html')

def RegisterView(request):
    form = UserDataForm(request.POST)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        second_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

    return render(request, 'register.html', {'form': form})

def LoginView(request):
    return render(request, 'login.html')