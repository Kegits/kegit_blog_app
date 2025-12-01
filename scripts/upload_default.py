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

    # Check if Cloudinary is configured
    if not hasattr(settings, 'CLOUDINARY_CLOUD_NAME') or not settings.CLOUDINARY_CLOUD_NAME:
        print("ERROR: Cloudinary not configured. Set CLOUDINARY_CLOUD_NAME in environment.")
        return

    image_path = os.path.join(settings.MEDIA_ROOT, 'default.jpg')

    if not os.path.exists(image_path):
        print(f"ERROR: default.jpg not found at {image_path}")
        return

    try:
        result = cloudinary.uploader.upload(
            image_path,
            public_id='profile_pics/default.jpg',
            folder='profile_pics',
            resource_type='image',
            overwrite=True,
        )
        print(f"✓ Uploaded default.jpg to Cloudinary: {result.get('public_id')}")
    except Exception as e:
        print(f"ERROR uploading default.jpg: {str(e)}")

if __name__ == '__main__':
    upload_default_image()
