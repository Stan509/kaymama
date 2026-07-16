from django.test import TestCase
from django.contrib.auth import get_user_model

class AccountsModelTests(TestCase):
    def test_create_customer(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='johndoe',
            email='johndoe@example.com',
            password='secretpassword123',
            role=User.ROLE_CUSTOMER
        )
        self.assertEqual(user.role, User.ROLE_CUSTOMER)
        self.assertFalse(user.is_staff_member)
        self.assertEqual(str(user), "johndoe (Client)")

    def test_create_manager(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='managerbob',
            email='bob@example.com',
            password='secretpassword123',
            role=User.ROLE_MANAGER
        )
        self.assertEqual(user.role, User.ROLE_MANAGER)
        self.assertTrue(user.is_staff_member)
