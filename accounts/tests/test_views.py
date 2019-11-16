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

    def test_adds_success_message(self):
        # # 'follow=True' tells the client to get the page it was redirected to.
        response = self.client.post('/accounts/send_login_email', data={
            'email': 'edith@example.com'
        }, follow=True)

        message = list(response.context['messages'])[0]
        self.assertEqual(
            message.message,
            "Check your email, we've sent you a link you can use to log in."
        )
        self.assertEqual(message.tags, "success")

    @patch('accounts.views.messages')
    def test_adds_success_message_with_mocks(self, mock_messages):
        # # This is an example where testing w/ mocks can leave us coupled to the
        # # implementation.
        # # This test enforces that we use the shortcut method: 'messages.success'
        # # If we tried to send the message with 'messages.add_message(.., messages.SUCCESS, ..)
        # # while the code would work as expected, the test would fail.
        # # The above test, without mocks, does not have this problem.
        # # However, sometimes getting something like the version above to work in the first
        # # place is such a hassle that using mocks remains the pragmatic choice.
        response = self.client.post('/accounts/send_login_email', data={
            'email': 'edith@example.com'
        })

        mock_messages.success.assert_called_once()
        ((_request, msg_sent), _kwargs) = mock_messages.success.call_args

        self.assertEqual(
            msg_sent,
            "Check your email, we've sent you a link you can use to log in."
        )
