from django.test import TestCase
from django.core import mail
from django.core.mail import send_mail
from unittest.mock import patch
from unittest.mock import ANY
import accounts.views


class SendLoginEmailViewTest(TestCase):
    def setUp(self):
        self.original_send_mail = accounts.views.send_mail

    def tearDown(self):
        accounts.views.send_mail = self.original_send_mail

    def test_redirects_to_home_page(self):
        response = self.client.post('/accounts/send_login_email', data={
            'email': 'edith@example.com'
        })
        self.assertRedirects(response, '/')

    @patch('accounts.views.send_mail')
    def test_sends_mail_to_address_from_post(self, mock_send_mail):
        self.client.post('/accounts/send_login_email', data={
            'email': 'edith@example.com'
        })

        mock_send_mail.assert_called_once()
        (subject, _body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertEqual(subject, 'Your login link for Superlists')
        self.assertEqual(from_email, 'noreply@superlists')
        self.assertEqual(to_list, ['edith@example.com'])

    def test_sends_mail_to_address_from_post_DJANGO_MOCK(self):
        self.client.post('/accounts/send_login_email', data={
            'email': 'edith@example.com'
        })

        self.assertEqual(len(mail.outbox), 1)
        mail_sent = mail.outbox[0]
        self.assertEqual(mail_sent.subject, 'Your login link for Superlists')
        self.assertEqual(mail_sent.from_email, 'noreply@superlists')
        self.assertEqual(mail_sent.to, ['edith@example.com'])
