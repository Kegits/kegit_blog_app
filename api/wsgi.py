import os
import sys

# Ensure project root is on sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Set the Django settings module if not already set by environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coolweb.settings')

# Import and expose the WSGI application for the serverless runtime
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# Use serverless-wsgi to adapt the WSGI app to the serverless platform's
# invocation shape if available. If not available, fall back to returning
# the WSGI application object (some runtimes may still accept it).
try:
    from serverless_wsgi import handle_request
except Exception:
    handle_request = None


def handler(event, context=None):
    """Vercel and other serverless platforms call this handler.

    If `serverless_wsgi` is installed we delegate to it; otherwise return
    the raw WSGI application (best effort fallback).
    """
    if handle_request:
        return handle_request(application, event, context)

    # Fallback: some runtimes expect a callable — return a minimal bridge
    # This is a very small fallback and may not work for all providers.
    # It exists to avoid import-time failures when serverless-wsgi isn't present.
    def _wsgi_fallback(environ, start_response):
        return application(environ, start_response)

    return _wsgi_fallback
