from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Conversation(models.Model):
    first_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_as_first_user',
    )
    second_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_as_second_user',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['first_user', 'second_user'],
                name='unique_direct_conversation_pair',
            ),
            models.CheckConstraint(
                condition=~Q(first_user=F('second_user')),
                name='direct_conversation_users_differ',
            ),
        ]

    @classmethod
    def get_or_create_between(cls, user_a, user_b):
        if user_a.pk == user_b.pk:
            raise ValueError('A conversation requires two different users.')

        first_user, second_user = sorted((user_a, user_b), key=lambda user: user.pk)
        return cls.objects.get_or_create(
            first_user=first_user,
            second_user=second_user,
        )

    def other_user(self, user):
        if user.pk == self.first_user_id:
            return self.second_user
        if user.pk == self.second_user_id:
            return self.first_user
        raise ValueError('The user is not a participant in this conversation.')

    def __str__(self):
        return f'{self.first_user} and {self.second_user}'


class DirectMessage(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_direct_messages',
    )
    body = models.CharField(max_length=4000)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['sent_at']
        indexes = [
            models.Index(
                fields=['conversation', '-sent_at'],
                name='dm_conversation_sent_idx',
            ),
        ]

    def save(self, *args, **kwargs):
        if self.sender_id not in (
            self.conversation.first_user_id,
            self.conversation.second_user_id,
        ):
            raise ValueError('Only conversation participants can send messages.')

        super().save(*args, **kwargs)
        Conversation.objects.filter(pk=self.conversation_id).update(
            updated_at=timezone.now(),
        )

    def __str__(self):
        return f'Message from {self.sender} at {self.sent_at}'
