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

# Some serverless runtimes will look for a callable named `handler`.
# Provide a thin adapter if needed (keeps compatibility with different runtimes).
def handler(request, context=None):
    return application(request.environ, lambda *args: None)
