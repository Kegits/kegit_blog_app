import os
import tempfile
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coolweb.settings')
import django
django.setup()

from django.contrib.auth.models import User
from users.models import Profile
import cloudinary.uploader
from PIL import Image


def make_temp_image(path):
    img = Image.new('RGB', (100, 100), color=(255, 0, 0))
    img.save(path, 'JPEG')


def main():
    # create temp image
    tmpdir = tempfile.gettempdir()
    local_path = os.path.join(tmpdir, 'test_cloudinary_upload.jpg')
    make_temp_image(local_path)
    print('Local test image created at', local_path)

    # Upload via cloudinary uploader
    try:
        res = cloudinary.uploader.upload(local_path, folder='profile_pics_test')
    except Exception as e:
        print('Cloudinary upload failed:', e)
        return

    print('Upload response keys:', list(res.keys()))
    print('Secure URL:', res.get('secure_url'))

    # Attach to a user/profile
    user = User.objects.first()
    if not user:
        user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        print('Created test user:', user.username)

    profile, created = Profile.objects.get_or_create(user=user)
    # Set the image field to the public_id so django-cloudinary-storage resolves URL
    public_id = res.get('public_id')
    if public_id:
        profile.image = public_id
        profile.save()
        print('Assigned uploaded image to profile. profile.image.url =', profile.image.url)
    else:
        print('No public_id returned; cannot assign to field.')


if __name__ == '__main__':
    main()
