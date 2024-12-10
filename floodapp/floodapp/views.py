from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, get_user_model
from django import forms
from django.conf import settings
from .form import UserDataForm
from django.contrib import messages

import templates




# User = get_user_model()
# def RegisterView(request):
#     form = UserDataForm(request.POST)
#     if request.method == 'POST':
#         # first_name = request.POST.get('first_name')
#         # second_name = request.POST.get('last_name')
#         # email = request.POST.get('email')
#         # password = request.POST.get('password')
#         var = form.save(commit=False)
#         var.is_customer = True
#         var.save()
#         return redirect('login')

#     return render(request, 'register.html', {'form': form})


UserData = get_user_model()

def RegisterView(request):
    if request.method == 'POST':
        form = UserDataForm(request.POST)
        if form.is_valid():
            var = form.save(commit=False)
            var.is_customer = True
            var.save()
            messages.success(request, 'Account created. Please log in')
            return redirect('login')
        else:
            messages.warning(request, 'Something went wrong. Please check form errors') 
            print('pizda')
            return redirect('register')
    else:
        print('hui')
        form = UserDataForm()
        context = {'form': form}
        return render (request, 'register.html', context)


def Home(request):
    return render(request, 'index.html')

def LoginView(request):
    return render(request, 'login.html')
