from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
import json

class TestViews(TestCase):
    def test_register_user_view(self):
        response = self.client.get(reverse('register-customer'))
        self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, '')