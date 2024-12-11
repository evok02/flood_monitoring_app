from django.urls import path
from . import views

urlpatterns = [
    path('register-customer/', views.register_customer, name='register-customer'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('password_reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password_reset/confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
]