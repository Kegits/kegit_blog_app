"""
WSGI config for coolweb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coolweb.settings')

application = get_wsgi_application()

# For Vercel: expose handler that wraps the WSGI application
def handler(request, context=None):
    """Handler for Vercel serverless runtime."""
    try:
        from serverless_wsgi import handle_request
        return handle_request(application, request, context)
    except Exception:
        # Fallback: return WSGI app directly
        return application
