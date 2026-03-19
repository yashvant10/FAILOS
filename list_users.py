import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'failos_project.settings')
django.setup()

from failures.models import User

users = User.objects.all()
print(f"Total Users: {users.count()}")
for u in users:
    print(f"USER_FOUND: {u.username} | {u.email}")
