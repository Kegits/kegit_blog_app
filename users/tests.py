import io
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from coolweb.storage import CloudinaryDirectStorage
from portfolio.models import Post
from users.context_processors import profile_image_fallback
from users.models import Profile


class CloudinaryStorageTests(SimpleTestCase):
    def test_default_profile_fallback_uses_cloudinary_url(self):
        with override_settings(CLOUDINARY_CLOUD_NAME='test-cloud'):
            context = profile_image_fallback(None)

        self.assertEqual(
            context['profile_image_fallback_url'],
            'https://res.cloudinary.com/test-cloud/image/upload/profile_pics/default',
        )

    @patch(
        'coolweb.storage.cloudinary.config',
        return_value=SimpleNamespace(cloud_name='test-cloud'),
    )
    def test_profile_default_image_uses_cloudinary_asset(self, _config):
        default_image = Profile._meta.get_field('image').get_default()
        self.assertEqual(default_image, 'profile_pics/default')
        self.assertEqual(
            CloudinaryDirectStorage().url(default_image),
            'https://res.cloudinary.com/test-cloud/image/upload/profile_pics/default',
        )

    def test_default_storage_matches_cloudinary_configuration(self):
        expected_backend = (
            'coolweb.storage.CloudinaryDirectStorage'
            if settings.CLOUDINARY_CLOUD_NAME
            else 'django.core.files.storage.FileSystemStorage'
        )

        self.assertEqual(settings.STORAGES['default']['BACKEND'], expected_backend)

    @patch(
        'coolweb.storage.cloudinary.config',
        return_value=SimpleNamespace(cloud_name='test-cloud'),
    )
    @patch(
        'coolweb.storage.cloudinary.uploader.upload',
        return_value={'public_id': 'profile_pics/test-image'},
    )
    def test_save_uploads_and_returns_cloudinary_public_id(self, upload, _config):
        storage = CloudinaryDirectStorage()

        name = storage.save(
            'profile_pics/test-image.jpg',
            ContentFile(b'test image content'),
        )

        self.assertEqual(name, 'profile_pics/test-image')
        self.assertEqual(
            storage.url(name),
            'https://res.cloudinary.com/test-cloud/image/upload/profile_pics/test-image',
        )
        self.assertEqual(upload.call_args.kwargs['folder'], 'profile_pics')
        self.assertEqual(upload.call_args.kwargs['public_id'], 'test-image')
        self.assertEqual(upload.call_args.kwargs['resource_type'], 'auto')


class ProfileUploadFlowTests(TestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_dir.cleanup)
        settings_override = override_settings(
            MEDIA_ROOT=self.media_dir.name,
            STORAGES={
                'default': {
                    'BACKEND': 'django.core.files.storage.FileSystemStorage',
                },
                'staticfiles': {
                    'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
                },
            },
        )
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        self.user = User.objects.create_user(
            username='upload-test',
            email='upload-test@example.invalid',
            password='Temporary-test-password-9021',
        )
        self.client.force_login(self.user)

    def test_new_user_gets_default_profile_image(self):
        profile = Profile.objects.get(user=self.user)

        self.assertEqual(profile.image.name, 'profile_pics/default')

    def test_default_profile_image_appears_where_user_is_shown(self):
        post = Post.objects.create(
            title='Profile avatar test',
            content='Checking author avatars across post pages.',
            author=self.user,
        )
        image_url = self.user.profile.image.url
        pages = (
            reverse('portfolio-home'),
            reverse('user-posts', kwargs={'username': self.user.username}),
            reverse('post-detail', kwargs={'pk': post.pk}),
        )

        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, f'src="{image_url}"')

    def test_default_profile_image_appears_in_authenticated_navigation(self):
        response = self.client.get(reverse('portfolio-home'))

        self.assertContains(response, 'class="profile-nav-img"')
        self.assertContains(response, self.user.profile.image.url)

    def test_profile_image_upload_persists_to_local_storage(self):
        image_buffer = io.BytesIO()
        Image.new('RGB', (8, 8), color='blue').save(image_buffer, format='JPEG')

        response = self.client.post(
            reverse('profile'),
            {
                'username': self.user.username,
                'email': self.user.email,
                'theme_mode': Profile.ThemeMode.SYSTEM,
                'profile_background': Profile.BackgroundStyle.FOREST,
                'chat_background': Profile.BackgroundStyle.FOREST,
                'image': SimpleUploadedFile(
                    'smoke.jpg',
                    image_buffer.getvalue(),
                    content_type='image/jpeg',
                ),
            },
        )

        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        image_name = self.user.profile.image.name
        self.assertTrue(image_name.startswith('profile_pics/'))
        self.assertTrue((Path(self.media_dir.name) / image_name).is_file())

    def test_profile_appearance_preferences_are_saved_and_applied(self):
        response = self.client.post(
            reverse('profile'),
            {
                'username': self.user.username,
                'email': self.user.email,
                'theme_mode': Profile.ThemeMode.DARK,
                'profile_background': Profile.BackgroundStyle.OCEAN,
                'chat_background': Profile.BackgroundStyle.MIDNIGHT,
            },
        )

        self.assertRedirects(response, reverse('profile'))
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.theme_mode, Profile.ThemeMode.DARK)
        self.assertEqual(
            self.user.profile.profile_background,
            Profile.BackgroundStyle.OCEAN,
        )
        self.assertEqual(
            self.user.profile.chat_background,
            Profile.BackgroundStyle.MIDNIGHT,
        )

        home_response = self.client.get(reverse('portfolio-home'))
        self.assertContains(home_response, '<html lang="en" data-theme="dark">')

        Post.objects.create(
            title='A themed story',
            content='Its author chose an ocean profile background.',
            author=self.user,
        )
        stories_response = self.client.get(
            reverse('user-posts', kwargs={'username': self.user.username})
        )
        self.assertContains(
            stories_response,
            'class="hero-panel profile-hero profile-theme-ocean"',
        )


class LogoutFlowTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user(
            username='logout-test',
            email='logout-test@example.invalid',
            password='Temporary-test-password-9021',
        )
        self.client.force_login(self.user)

    def test_navbar_logout_post_ends_session_and_renders_confirmation(self):
        home_response = self.client.get(reverse('portfolio-home'))
        self.assertContains(home_response, 'class="nav-logout-form"')
        csrf_token = self.client.cookies['csrftoken'].value
        response = self.client.post(
            reverse('logout'),
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You’re signed out.')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertRedirects(
            self.client.get(reverse('profile')),
            f'{reverse("login")}?next={reverse("profile")}',
        )
