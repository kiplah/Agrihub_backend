import os
import django
import sys

# Add the project directory to the sys.path
sys.path.append('d:\\agric\\Agro-Mart\\backend_django')

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agromart.settings')

# Setup Django
django.setup()

from users.models import User

email = 'kiplahvictor27@gmail.com'
users = User.objects.filter(email=email).order_by('-date_joined')

if users.count() > 1:
    print(f"Found {users.count()} users with email {email}. Keeping the latest one.")
    # Keep the first one (latest due to order_by), delete the rest
    for user in users[1:]:
        print(f"Deleting user {user.username} (ID: {user.id})")
        user.delete()
    print("Cleanup complete.")
else:
    print("No duplicates found.")
