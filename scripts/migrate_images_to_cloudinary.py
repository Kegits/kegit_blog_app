import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coolweb.settings')
import django
django.setup()

from users.models import Profile
import cloudinary.uploader
from django.conf import settings


def migrate_profile_images():
    """
    Migrate existing profile images from local storage to Cloudinary.
    """
    print("Starting migration of profile images to Cloudinary...")

    # Check if Cloudinary is configured
    if not hasattr(settings, 'CLOUDINARY_CLOUD_NAME') or not settings.CLOUDINARY_CLOUD_NAME:
        print("ERROR: Cloudinary not configured. Set CLOUDINARY_CLOUD_NAME in environment.")
        return

    profiles = Profile.objects.all()
    migrated_count = 0

    for profile in profiles:
        try:
            # Skip if already a Cloudinary URL (contains 'res.cloudinary.com')
            if 'res.cloudinary.com' in str(profile.image):
                print(f"Skipping {profile.user.username}: already on Cloudinary")
                continue

            # Get the local file path
            image_path = os.path.join(settings.MEDIA_ROOT, str(profile.image))

            if not os.path.exists(image_path):
                print(f"WARNING: Local file not found for {profile.user.username}: {image_path}")
                continue

            print(f"Uploading {profile.user.username}'s image: {image_path}")

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                image_path,
                folder='profile_pics',
                public_id=f"{profile.user.username}_profile",
                resource_type='image',
                overwrite=True,
                unique_filename=False,
            )

            # Update the profile with the new Cloudinary public_id
            public_id = result.get('public_id')
            if public_id:
                profile.image = public_id
                profile.save()
                migrated_count += 1
                print(f"✓ Migrated {profile.user.username}: {public_id}")
            else:
                print(f"ERROR: No public_id returned for {profile.user.username}")

        except Exception as e:
            print(f"ERROR migrating {profile.user.username}: {str(e)}")

    print(f"Migration complete. Migrated {migrated_count} profile images.")


if __name__ == '__main__':
    migrate_profile_images()
