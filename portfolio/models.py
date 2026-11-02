from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='post_comments',
    )
    body = models.CharField(max_length=2000)
    mentions = models.ManyToManyField(
        User,
        through='CommentMention',
        related_name='mentioned_in_comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'


class CommentMention(models.Model):
    comment = models.ForeignKey(
        PostComment,
        on_delete=models.CASCADE,
        related_name='mention_links',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment_mentions',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['comment', 'user'],
                name='unique_user_mention_per_comment',
            ),
        ]


class MentionNotification(models.Model):
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mention_notifications',
    )
    comment = models.ForeignKey(
        PostComment,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['recipient', 'comment'],
                name='unique_mention_notification',
            ),
        ]

    def __str__(self):
        return f'Mention for {self.recipient} by {self.comment.author}'