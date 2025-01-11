from accounts.models import User
from django.test import TestCase

class TestModels(TestCase):
    def test_register_user_model(self):
        user = User.objects.create_user(username='test_register', email='lolkek12@gmail.com')
        user.set_password('password03!')
        user.save()
        self.assertEqual(str(user), 'lolkek12@gmail.com')

