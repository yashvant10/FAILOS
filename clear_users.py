import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'failos_project.settings')
django.setup()

from failures.models import User

users = User.objects.all()
count = users.count()
users.delete()
print(f"Deleted {count} users. Database is now clean.")
