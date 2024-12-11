from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from .form import RegisteredCustomerForm
from django.http import JsonResponse

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
            if 'email' in form.errors and 'User with this Email already exists.' in form.errors['email']:
                messages.warning(request, 'User with this email already exists.')
                return render(request, 'register-customer.html', {'form': form}, status=409)
            print("Form errors:", form.errors)
            print("first else statement")
            messages.warning(request, 'Something went wrong. Please check form errors')

            return render(request, 'register-customer.html', {'form': form})
    else:
        print('second else statement')  # Debugging
        form = RegisteredCustomerForm()
        context = {'form': form}
        return render(request, 'register-customer.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect('map')
        else:
            if user is None:
                messages.warning(request, 'User not found. If you have not registered yet, proceed to sign up')
                return render(request, 'login.html', status=400)
            messages.warning(request, 'Something went wrong. Please check form errors')
            return redirect('login', status=400)
    else:
        return render(request, 'login.html')

def logout_user(request):
    logout(request)
    messages.success(request, 'Active session ended. Log in to continue')
    return redirect('login')


