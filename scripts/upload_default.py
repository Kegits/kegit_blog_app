import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coolweb.settings')
import django
django.setup()

import cloudinary.uploader
from django.conf import settings

def upload_default_image():
    """
    Upload default.jpg to Cloudinary with specific public_id.
    """
    print("Uploading default.jpg to Cloudinary...")

    if not settings.CLOUDINARY_CLOUD_NAME:
        raise RuntimeError("Cloudinary is not configured.")

    image_path = os.path.join(settings.MEDIA_ROOT, 'default.jpg')

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"default.jpg not found at {image_path}")

    try:
        result = cloudinary.uploader.upload(
            image_path,
            public_id='profile_pics/default',
            resource_type='image',
            overwrite=True,
        )
    except Exception as exc:
        raise RuntimeError("Cloudinary upload of the default profile image failed.") from exc

    print(f"Uploaded default.jpg to Cloudinary: {result.get('public_id')}")

if __name__ == '__main__':
    upload_default_image()
