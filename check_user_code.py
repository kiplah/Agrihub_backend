import os
import django
import sys

# Add the project directory to the sys.path
sys.path.append('d:\\agric\\Agro-Mart\\backend_django')

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agromart.settings')

# Setup Django
django.setup()

from api.models import User

try:
    email = 'kiplahvictor27@gmail.com'
    user = User.objects.get(email=email)
    print(f"User: {user.email}")
    print(f"Stored Verification Code: '{user.verification_code}'") # Quotes to see whitespace
except User.DoesNotExist:
    print(f"User with email {email} not found.")
except Exception as e:
    print(f"Error: {e}")
