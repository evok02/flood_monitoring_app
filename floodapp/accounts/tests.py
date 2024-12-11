from django.test import TestCase
from django.contrib.auth import get_user_model

# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth.models import Group
from django.urls import reverse

class AdminOnlyPageTestCase(TestCase):
    def setUp(self):

        User = get_user_model()
        # Ensure "admin" group exists
        admin_group, created = Group.objects.get_or_create(name="admin")

        # Create the admin user and assign to the "admin" group
        self.admin_user = User.objects.create_user(username="testusertest@gmail.com", password="TestUserPassword13+")
        self.admin_user.groups.add(admin_group)

        # Create a client for making HTTP requests
        self.client = Client()

    def test_admin_only_page_access(self):
        # Log in as the admin user
        login_successful = self.client.login(username="testusertest@gmail.com", password="TestUserPassword13+")
        self.assertTrue(login_successful, "Admin user could not log in")

        # Access the admin-only page
        url = reverse("admin_only_page")  
        response = self.client.get(url)

        # Assertions
        self.assertEqual(response.status_code, 200, "Admin user should have access to this page")
        self.assertTemplateUsed(response, "admin_only_page.html", "Expected template was not used")
        self.assertContains(response, "If you see this page, you're admin", msg_prefix="Expected content not found")


class NonAdminUserAccessTestCase(TestCase):
    def setUp(self):
        # Get the custom user model
        User = get_user_model()

        # Create a non-admin user (not assigned to the "admin" group)
        self.non_admin_user = User.objects.create_user(username="notadmintestuser@gmail.com", password="TestUserPassword13+")

        # Create a client for making HTTP requests
        self.client = Client()

    def test_non_admin_user_access(self):
        # Log in as the non-admin user
        login_successful = self.client.login(username="notadmintestuser@gmail.com", password="TestUserPassword13+")
        self.assertTrue(login_successful, "Non-admin user could not log in")

        # Attempt to access the admin-only page
        url = reverse("admin_only_page")  
        response = self.client.get(url)

        # Assertions
        self.assertEqual(response.status_code, 200, "Non-admin user should not have access to this page")
        self.assertContains(response, "You are not authorized to view this page", msg_prefix="Expected unauthorized access message not found")
