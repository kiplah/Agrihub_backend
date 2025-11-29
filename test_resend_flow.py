import requests
import time

base_url = "http://127.0.0.1:8000"
email = "apitest@example.com"
password = "password123"

# 1. Signup
print("--- Signup ---")
signup_url = f"{base_url}/signup"
signup_payload = {
    "username": "apitest",
    "email": email,
    "password": password,
    "role": "buyer"
}
try:
    resp = requests.post(signup_url, json=signup_payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Signup Error: {e}")

# 2. Check Code (Manual check via script output later, but here we just proceed)

# 3. Resend Code
print("\n--- Resend Code ---")
resend_url = f"{base_url}/users/resend_verification/" # Note: ViewSet action url might be different
# Default router usually maps actions to /users/{pk}/action or similar, but I used @action(detail=False)
# So it should be /users/resend_verification/
# Let's check urls.py or try /api/users/resend_verification/

# Actually, I used router.register(r'users', UserViewSet)
# So it should be /users/resend_verification/ if I didn't set url_path
# Let's try /users/resend_verification/
resend_payload = {"email": email}

try:
    resp = requests.post(f"{base_url}/users/resend_verification/", json=resend_payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Resend Error: {e}")
