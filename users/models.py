from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    class ThemeMode(models.TextChoices):
        SYSTEM = 'system', 'Use device setting'
        LIGHT = 'light', 'Light'
        DARK = 'dark', 'Dark'

    class BackgroundStyle(models.TextChoices):
        FOREST = 'forest', 'Forest'
        OCEAN = 'ocean', 'Ocean'
        SUNSET = 'sunset', 'Sunset'
        MIDNIGHT = 'midnight', 'Midnight'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(
        default='profile_pics/default',
        upload_to='profile_pics'
    )
    theme_mode = models.CharField(
        max_length=10,
        choices=ThemeMode.choices,
        default=ThemeMode.SYSTEM,
    )
    profile_background = models.CharField(
        max_length=10,
        choices=BackgroundStyle.choices,
        default=BackgroundStyle.FOREST,
    )
    chat_background = models.CharField(
        max_length=10,
        choices=BackgroundStyle.choices,
        default=BackgroundStyle.FOREST,
    )

    def __str__(self):
        return f'{self.user.username} Profile'
