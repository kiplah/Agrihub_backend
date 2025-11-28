import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_signup_verify():
    print("Testing Signup...")
    # Use a random email to avoid "already exists" error if possible, or handle it
    timestamp = int(time.time())
    email = f"test{timestamp}@example.com"
    
    data = {
        "username": f"user{timestamp}",
        "email": email,
        "password": "password123",
        "role": "buyer"
    }
    
    # 1. Signup
    response = requests.post(f"{BASE_URL}/signup", json=data)
    if response.status_code == 201:
        print("Signup Successful (201 Created)")
    else:
        print(f"Signup Failed: {response.status_code} {response.text}")
        return False

    # 2. Verify
    print("Testing Verify...")
    verify_data = {
        "email": email,
        "code": "123456" # Mock code
    }
    response = requests.post(f"{BASE_URL}/verify", json=verify_data)
    
    if response.status_code == 200:
        print("Verify Successful (200 OK)")
        json_resp = response.json()
        if "event" in json_resp and "token" in json_resp["event"]:
             print(f"Token received: {json_resp['event']['token'][:20]}...")
             return True
        else:
             print(f"Verify response missing token: {json_resp}")
             return False
    else:
        print(f"Verify Failed: {response.status_code} {response.text}")
        return False

if __name__ == "__main__":
    test_signup_verify()
