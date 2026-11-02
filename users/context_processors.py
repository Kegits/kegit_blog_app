from django.conf import settings


def profile_image_fallback(_request):
    cloud_name = settings.CLOUDINARY_CLOUD_NAME
    if cloud_name:
        image_url = (
            f'https://res.cloudinary.com/{cloud_name}/image/upload/profile_pics/default'
        )
    else:
        image_url = f'{settings.MEDIA_URL.rstrip("/")}/profile_pics/default.jpg'

    return {'profile_image_fallback_url': image_url}
