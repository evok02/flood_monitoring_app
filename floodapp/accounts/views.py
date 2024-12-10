from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from .form import RegisteredCustomerForm

# Create your views here.

User = get_user_model()

def register_customer(request):
    print(f"Request method: {request.method}")  # Debugging
    if request.method == 'POST':
        print('POST request detected')  # Check if this prints
        form = RegisteredCustomerForm(request.POST)
        if form.is_valid():
            var = form.save(commit=False)
            var.is_customer = True
            var.username = var.email
            var.save()
            messages.success(request, 'Account created. Please log in')
            return redirect('login')
        else:
            messages.warning(request, 'Something went wrong. Please check form errors')
            return redirect('register-customer')
    else:
        print('GET request detected')  # Debugging
        form = RegisteredCustomerForm()
        context = {'form': form}
        return render(request, 'register-customer.html', context)


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect('map')
        else:
            messages.warning(request, 'Something went wrong. Please check form errors')
            return redirect('login')
    else:
        return render(request, 'login.html')

def logout_user(request):
    logout(request)
    messages.success(request, 'Active session ended. Log in to continue')
    return redirect('login')

    