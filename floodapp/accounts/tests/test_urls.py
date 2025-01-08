from django.test import SimpleTestCase
from django.urls import reverse, resolve
from accounts.views import register_customer, login_user, logout_user

class TestUrls(SimpleTestCase):
    def test_register_url(self):
        url = reverse('register-customer')
        self.assertEqual(resolve(url).func, register_customer)

    def test_login_url(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func, login_user)

    def test_logout_url(self):
        url = reverse('logout')
        self.assertEqual(resolve(url).func, logout_user)