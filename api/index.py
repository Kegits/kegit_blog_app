import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coolweb.settings')

import django
django.setup()

# Import WSGI application
from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
