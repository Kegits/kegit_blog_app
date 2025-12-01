from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import cloudinary

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Use a Cloudinary-hosted default image URL or a local filename if uploaded to Cloudinary
    # If using a filename, ensure 'default.jpg' exists in your Cloudinary account.
    # For now, using a simple placeholder—upload default.jpg to Cloudinary and use that filename.
    image = models.ImageField(
        default='profile_pics/default',  # Cloudinary public_id for default image
        upload_to='profile_pics'
    )

    def __str__(self):
        return f'{self.user.username} Profile'
    
    # def save(self, *args, **kwargs):
    #    super().save(*args, **kwargs)

    #   img = Image.open(self.image.path)

    #   if img.height > 300 or img.width > 300:
    #       output_size = (300, 300)
    #      img.thumbnail(output_size)
    #      img.save(self.image.path)