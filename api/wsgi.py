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

# For Vercel: expose the application as a handler
# Vercel will call this with (event, context) arguments
def handler(event, context):
    """Vercel serverless handler that wraps the WSGI application."""
    try:
        from serverless_wsgi import handle_request
        return handle_request(application, event, context)
    except Exception:
        # Fallback: return the application object for Vercel to handle
        return application
