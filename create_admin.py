import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "failos_project.settings")
django.setup()

from failures.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@admin.com', 'admin123')
    print("Created superuser: admin / admin123")
else:
    print("Superuser 'admin' already exists")
