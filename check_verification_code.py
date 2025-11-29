import os
import django
import sys
from django.utils import timezone

# Add the project directory to the sys.path
sys.path.append('d:\\agric\\Agro-Mart\\backend_django')

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agromart.settings')

# Setup Django
django.setup()

from api.models import User

if len(sys.argv) < 2:
    print("Usage: python check_verification_code.py <email>")
    sys.exit(1)

email = sys.argv[1]

try:
    user = User.objects.get(email=email)
    print(f"User: {user.email}")
    print(f"Code: {user.verification_code}")
    print(f"Expires: {user.verification_code_expires_at}")
    if user.verification_code_expires_at:
        time_left = user.verification_code_expires_at - timezone.now()
        print(f"Time left: {time_left}")
    else:
        print("Time left: None")
except User.DoesNotExist:
    print(f"User with email {email} not found.")
except Exception as e:
    print(f"Error: {e}")
