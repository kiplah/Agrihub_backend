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

try:
    # Get the latest user
    user = User.objects.latest('date_joined')
    print(f"Latest User: {user.email}")
    print(f"Verification Code: {user.verification_code}")
except User.DoesNotExist:
    print("No users found.")
except Exception as e:
    print(f"Error: {e}")
