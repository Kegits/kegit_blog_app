from django.core.management.base import BaseCommand
from users.models import Profile
import cloudinary.uploader
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Migrate local profile images to Cloudinary'

    def handle(self, *args, **options):
        profiles = Profile.objects.all()
        for profile in profiles:
            if profile.image and hasattr(profile.image, 'path'):
                # Check if it's a local file
                if os.path.exists(profile.image.path):
                    self.stdout.write(f"Uploading {profile.image.name} for user {profile.user.username}")
                    try:
                        # Upload to Cloudinary
                        result = cloudinary.uploader.upload(
                            profile.image.path,
                            folder='profile_pics',
                            public_id=Path(profile.image.name).stem
                        )
                        # Update the profile to use Cloudinary public_id
                        profile.image = result['public_id']
                        profile.save()
                        self.stdout.write(
                            self.style.SUCCESS(f"Successfully migrated {profile.user.username}'s image")
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Failed to upload {profile.image.name}: {e}")
                        )
                else:
                    self.stdout.write(f"File {profile.image.path} does not exist for {profile.user.username}")
            else:
                self.stdout.write(f"No image for {profile.user.username}")
