from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Conversation, DirectMessage


class PrivateConversationTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(
            username='alice',
            password='Temporary-test-password-9021',
        )
        self.bob = User.objects.create_user(
            username='bob',
            password='Temporary-test-password-9021',
        )
        self.carol = User.objects.create_user(
            username='carol',
            password='Temporary-test-password-9021',
        )

    def test_authenticated_user_can_start_and_exchange_private_messages(self):
        self.client.force_login(self.alice)

        response = self.client.post(
            reverse('messaging:start'),
            {'username': self.bob.username},
        )
        conversation = Conversation.objects.get()
        self.assertRedirects(
            response,
            reverse('messaging:conversation', kwargs={'pk': conversation.pk}),
        )

        response = self.client.post(
            reverse('messaging:conversation', kwargs={'pk': conversation.pk}),
            {'body': 'A private hello'},
        )

        self.assertRedirects(
            response,
            reverse('messaging:conversation', kwargs={'pk': conversation.pk}),
        )
        message = DirectMessage.objects.get()
        self.assertEqual(message.sender, self.alice)
        self.assertEqual(message.body, 'A private hello')

        self.client.force_login(self.bob)
        self.bob.profile.chat_background = 'ocean'
        self.bob.profile.save(update_fields=['chat_background'])
        inbox_response = self.client.get(reverse('messaging:inbox'))
        self.assertContains(inbox_response, 'A private hello')
        self.assertContains(inbox_response, 'nav-count">1')
        message.refresh_from_db()
        self.assertIsNone(message.read_at)

        response = self.client.get(
            reverse('messaging:conversation', kwargs={'pk': conversation.pk})
        )
        self.assertContains(response, 'A private hello')
        self.assertContains(response, 'direct-message-list chat-theme-ocean')
        message.refresh_from_db()
        self.assertIsNotNone(message.read_at)

    def test_nonparticipant_cannot_view_or_send_in_conversation(self):
        conversation, _created = Conversation.get_or_create_between(
            self.alice,
            self.bob,
        )
        self.client.force_login(self.carol)

        url = reverse('messaging:conversation', kwargs={'pk': conversation.pk})
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(
            self.client.post(url, {'body': 'Trying to read private chat'}).status_code,
            404,
        )
        self.assertFalse(DirectMessage.objects.exists())

    def test_direct_message_model_rejects_nonparticipant_sender(self):
        conversation, _created = Conversation.get_or_create_between(
            self.alice,
            self.bob,
        )

        with self.assertRaises(ValueError):
            DirectMessage.objects.create(
                conversation=conversation,
                sender=self.carol,
                body='This must not be sent',
            )

    def test_same_pair_reuses_one_conversation_in_either_order(self):
        first, created = Conversation.get_or_create_between(self.alice, self.bob)
        second, created_again = Conversation.get_or_create_between(self.bob, self.alice)

        self.assertTrue(created)
        self.assertFalse(created_again)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(Conversation.objects.count(), 1)

    def test_cannot_start_conversation_with_self(self):
        self.client.force_login(self.alice)

        response = self.client.post(
            reverse('messaging:start'),
            {'username': self.alice.username},
        )

        self.assertRedirects(response, reverse('messaging:inbox'))
        self.assertFalse(Conversation.objects.exists())

    def test_anonymous_user_cannot_open_inbox_or_start_chat(self):
        inbox_response = self.client.get(reverse('messaging:inbox'))
        start_response = self.client.post(
            reverse('messaging:start'),
            {'username': self.bob.username},
        )

        self.assertRedirects(
            inbox_response,
            f'{reverse("login")}?next={reverse("messaging:inbox")}',
        )
        self.assertRedirects(
            start_response,
            f'{reverse("login")}?next={reverse("messaging:start")}',
        )
        self.assertFalse(Conversation.objects.exists())
