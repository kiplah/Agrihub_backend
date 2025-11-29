import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agromart.settings')
django.setup()

from api.models import User

email = "kiplahvictor27@gmail.com"
print(f"Checking for user with email: '{email}'")

users = User.objects.filter(email=email)
print(f"Found {users.count()} users.")

for u in users:
    print(f"ID: {u.id}")
    print(f"Username: '{u.username}'")
    print(f"Email: '{u.email}'")
    print(f"Is Active: {u.is_active}")
    print(f"Verification Code: {u.verification_code}")
    print("-" * 20)

# Check for case-insensitive match
users_iexact = User.objects.filter(email__iexact=email)
print(f"Found {users_iexact.count()} users (case-insensitive).")
