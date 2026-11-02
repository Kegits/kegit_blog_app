from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import MentionNotification, Post, PostComment


class PostCommentTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='story-author',
            password='Temporary-test-password-9021',
        )
        self.commenter = User.objects.create_user(
            username='commenter',
            password='Temporary-test-password-9021',
        )
        self.post = Post.objects.create(
            title='Public story',
            content='A story for the community.',
            author=self.author,
        )
        self.comment_url = reverse('post-comment-create', kwargs={'pk': self.post.pk})

    def test_signed_in_comment_tags_and_notifies_mentioned_user(self):
        self.client.force_login(self.commenter)

        response = self.client.post(
            self.comment_url,
            {'body': 'Hello @story-author, great story!'},
        )

        comment = PostComment.objects.get(post=self.post)
        self.assertRedirects(response, self.post.get_absolute_url())
        self.assertEqual(list(comment.mentions.all()), [self.author])
        self.assertTrue(
            MentionNotification.objects.filter(
                recipient=self.author,
                comment=comment,
                read_at__isnull=True,
            ).exists()
        )

    def test_post_cards_show_activity_and_load_comment_text_on_demand(self):
        PostComment.objects.create(
            post=self.post,
            author=self.commenter,
            body='This reply should only appear after opening the conversation.',
        )

        response = self.client.get(reverse('portfolio-home'))

        self.assertContains(response, 'Conversation')
        self.assertContains(response, '1')
        self.assertContains(response, 'comment')
        self.assertContains(response, 'Active ')
        self.assertContains(response, 'class="story-grid"')
        self.assertContains(response, 'Read story')
        self.assertContains(response, 'Join conversation')
        self.assertContains(
            response,
            f'href="{self.post.get_absolute_url()}#comments-heading"',
        )
        self.assertNotContains(
            response,
            'This reply should only appear after opening the conversation.',
        )

        preview = self.client.get(
            reverse('post-comments-preview', kwargs={'pk': self.post.pk})
        )

        self.assertContains(
            preview,
            'This reply should only appear after opening the conversation.',
        )
        self.assertContains(preview, 'Join the conversation')

    def test_comment_preview_shows_only_three_latest_comments(self):
        for index in range(6):
            PostComment.objects.create(
                post=self.post,
                author=self.commenter,
                body=f'Reply {index}',
            )

        response = self.client.get(
            reverse('post-comments-preview', kwargs={'pk': self.post.pk})
        )

        self.assertContains(response, 'View all 6 comments')
        self.assertContains(
            response,
            '<article class="comment-card preview-comment">',
            count=3,
        )
        for index in range(3):
            self.assertNotContains(response, f'Reply {index}')
        for index in range(3, 6):
            self.assertContains(response, f'Reply {index}')
        self.assertContains(
            response,
            f'href="{self.post.get_absolute_url()}#comments-heading"',
        )

    def test_mentions_render_as_links_and_user_input_stays_escaped(self):
        comment = PostComment.objects.create(
            post=self.post,
            author=self.commenter,
            body='<script>alert(1)</script> @story-author',
        )
        comment.mentions.add(self.author)
        self.client.force_login(self.commenter)

        response = self.client.get(self.post.get_absolute_url())

        self.assertContains(
            response,
            f'href="{reverse("user-posts", kwargs={"username": self.author.username})}"',
        )
        self.assertContains(response, '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertNotContains(response, '<script>alert(1)</script>')

    def test_punctuation_after_mention_does_not_prevent_notification(self):
        self.client.force_login(self.commenter)

        response = self.client.post(
            self.comment_url,
            {'body': 'Hello @story-author. Welcome!'},
        )

        self.assertRedirects(response, self.post.get_absolute_url())
        self.assertTrue(
            MentionNotification.objects.filter(recipient=self.author).exists()
        )

    def test_anonymous_user_cannot_comment(self):
        response = self.client.post(self.comment_url, {'body': 'A comment'})

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={self.comment_url}',
        )
        self.assertFalse(PostComment.objects.filter(post=self.post).exists())

    def test_mentions_page_and_open_action_are_private_to_recipient(self):
        comment = PostComment.objects.create(
            post=self.post,
            author=self.commenter,
            body='@story-author take a look',
        )
        notification = MentionNotification.objects.create(
            recipient=self.author,
            comment=comment,
        )
        self.client.force_login(self.commenter)

        self.assertEqual(
            self.client.get(reverse('notifications')).status_code,
            200,
        )
        self.assertEqual(
            self.client.post(
                reverse('notification-open', kwargs={'pk': notification.pk})
            ).status_code,
            404,
        )

        self.client.force_login(self.author)
        response = self.client.post(
            reverse('notification-open', kwargs={'pk': notification.pk})
        )

        self.assertRedirects(response, self.post.get_absolute_url())
        notification.refresh_from_db()
        self.assertIsNotNone(notification.read_at)

    def test_blank_comment_is_rejected(self):
        self.client.force_login(self.commenter)

        response = self.client.post(self.comment_url, {'body': '   '})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(PostComment.objects.filter(post=self.post).exists())

# Create your tests here.
