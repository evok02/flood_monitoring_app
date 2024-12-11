from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
import json

class TestViews(TestCase):
    def test_register_user_view(self):
        response = self.client.get(reverse('register-customer'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register-customer.html')

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_should_signup_user(self):
        self.user ={
            'email': 'email1234@gmail.com',
            'password1': 'password12!',
            'password2': 'password12!'
        }
        response = self.client.post(reverse('register-customer'), self.user)
        self.assertEqual(response.status_code, 302)

    def test_should_not_signup(self):
        self.user ={
            'email': 'email1234@gmail.com',
            'password1': 'password12!',
            'password2': 'password12!'
        }
        self.client.post(reverse('register-customer'), self.user)
        response = self.client.post(reverse('register-customer'), self.user)
        self.assertEqual(response.status_code, 409)

    def test_user_login_success(self):
        self.user ={
            'email': 'email12345@gmail.com',
            'password1': 'password12!',
            'password2': 'password12!'
        }
        self.login_data = {
            'username': 'email12345@gmail.com',
            'password': 'password12!'
        }
        self.client.post(reverse('register-customer'), self.user)
        user = User.objects.filter(username='email12345@gmail.com').first()
        user.is_active = True
        user.save()
        response = self.client.post(reverse('login'), self.login_data)
        self.assertEqual(response.status_code, 302)

    def test_user_login_not_success(self):
        self.login_data = {
            'username': 'email123456@gmail.com',
            'password': 'password12!'
        }
        response = self.client.post(reverse('login'), self.login_data)
        self.assertEqual(response.status_code, 400)

