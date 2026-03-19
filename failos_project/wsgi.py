"""
WSGI config for failos_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

# Ensure the project root is in the path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'failos_project.settings')

# --- HELP VERCEL WITH STATIC FILES ---
from django.conf import settings
from django.core.management import call_command

# Only run collectstatic if the destination doesn't exist (save time)
if not os.path.exists(os.path.join(BASE_DIR, 'staticfiles')):
    try:
        call_command('collectstatic', '--noinput', '--clear')
    except Exception as e:
        print(f"Collectstatic failed: {e}")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Alias for Vercel
app = application
