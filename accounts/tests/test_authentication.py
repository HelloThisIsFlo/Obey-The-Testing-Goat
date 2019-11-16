from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.authentication import PasswordlessAuthenticationBackend
from accounts.models import Token

User = get_user_model()


class AuthenticateTest(TestCase):
    def setUp(self):
        self.backend = PasswordlessAuthenticationBackend()

    def test_returns_None_if_no_such_token(self):
        self.assertIsNone(self.backend.authenticate(uid='abcdoesntexist123'))

    def test_existing_user__returns_user_matching_email_associated_with_token_uid(self):
        email = 'edith@example.com'
        token = Token.objects.create(email=email)
        existing_user = User.objects.create(email=email)

        authenticated_user = self.backend.authenticate(uid=token.uid)

        self.assertEqual(authenticated_user, existing_user)

    def test_no_existing_user__creates_new_user_with_email_associated_with_token_uid(self):
        email = 'edith@example.com'
        token = Token.objects.create(email=email)
        self.assertEqual(User.objects.count(), 0)

        newly_created_and_authenticated_user = self.backend.authenticate(
            uid=token.uid
        )

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(
            newly_created_and_authenticated_user,
            User.objects.first()
        )
        self.assertEqual(
            newly_created_and_authenticated_user.email,
            'edith@example.com'
        )

    def test_get_existing_user(self):
        desired_user = User.objects.create(email='edith@example.com')
        User.objects.create(email='anotheruser@example.com')
        self.assertEqual(
            self.backend.get_user('edith@example.com'),
            desired_user
        )

    def test_get_missing_user(self):
        self.assertIsNone(self.backend.get_user('doesntexist@hello.com'))
