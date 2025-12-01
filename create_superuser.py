import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agromart.settings')
django.setup()

from users.models import User

username = "admin"
email = "admin@agromart.com"
password = "admin123"

try:
    user, created = User.objects.get_or_create(username=username, email=email)
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    
    action = "Created" if created else "Updated"
    print(f"SUCCESS: {action} superuser '{username}' with password '{password}'")

except Exception as e:
    print(f"ERROR: {e}")
