from django.conf import settings
import os
from django.http import JsonResponse

def storage_debug_view(request):
    return JsonResponse({
        'DEFAULT_FILE_STORAGE': getattr(settings, 'DEFAULT_FILE_STORAGE', None),
        'CLOUDINARY_CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
        'MEDIA_ROOT': getattr(settings, 'MEDIA_ROOT', None),
        'DEBUG': bool(getattr(settings, 'DEBUG', False)),
    })
