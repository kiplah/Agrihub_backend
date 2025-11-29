import requests
import sys
import os
import django

# Setup Django to access DB for code retrieval
sys.path.append('d:\\agric\\Agro-Mart\\backend_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agromart.settings')
django.setup()
from api.models import User

base_url = "http://127.0.0.1:8000"
email = "kiplahvictor27@gmail.com"
new_password = "newpassword456"

# 1. Forgot Password
print("--- Forgot Password ---")
forgot_url = f"{base_url}/users/forgot_password/"
try:
    resp = requests.post(forgot_url, json={"email": email})
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Forgot Error: {e}")

# 2. Get Code from DB
print("\n--- Get Code ---")
try:
    user = User.objects.get(email=email)
    code = user.reset_password_code
    print(f"Reset Code: {code}")
except Exception as e:
    print(f"DB Error: {e}")
    sys.exit(1)

# 3. Reset Password
print("\n--- Reset Password ---")
reset_url = f"{base_url}/users/reset_password/"
reset_payload = {
    "email": email,
    "code": code,
    "new_password": new_password
}
try:
    resp = requests.post(reset_url, json=reset_payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Reset Error: {e}")

# 4. Login with new password
print("\n--- Login ---")
login_url = f"{base_url}/login"
login_payload = {
    "email": email,
    "password": new_password
}
try:
    resp = requests.post(login_url, json=login_payload)
    if resp.status_code == 200:
        print("LOGIN SUCCESS")
    else:
        print(f"LOGIN FAILED: {resp.status_code} - {resp.text}")
except Exception as e:
    print(f"Login Error: {e}")
