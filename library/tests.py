from django.test import TestCase

from .models import User

# Create your tests here.

class TestUserRegisterView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test123', email='test@gmail.com')


    def test_user_created(self):
        self.assertEqual(self.user.username, 'test_user')
        self.assertEqual(self.user.email, 'test@gmail.com')