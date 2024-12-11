from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from .form import RegisteredCustomerForm
from django.contrib.auth.hashers import make_password

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


# Reset password views
# Take email input first
def password_reset_request_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            # Store the email in the session temporarily
            request.session['reset_email'] = email
            return redirect('password_reset_confirm')
        else:
            messages.error(request, "No account found with that email.")
    return render(request, 'password_reset.html')

# Reset password: take new password input
def password_reset_confirm_view(request):
    email = request.session.get('reset_email')
    if not email:
        # Redirect back if no email in session
        return redirect('password_reset_request')

    user = User.objects.filter(email=email).first()
    if not user:
        messages.error(request, "Invalid session. Please try again!")
        return redirect('password_reset_request')

    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if new_password == confirm_password:
            user.password = make_password(new_password)
            user.save()
            messages.success(request, "Password reset successfully! You can now log in.")
            # Clear the session email
            request.session.pop('reset_email', None)
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match. Please try again.")
    return render(request, 'password_reset_confirm.html')
