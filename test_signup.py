import requests
import json
import random

BASE_URL = "http://127.0.0.1:8000"

def test_signup():
    print("\n--- Testing Signup ---")
    url = f"{BASE_URL}/signup/"
    
    # Generate a random email to avoid "User already exists" for now, 
    # or use a specific one to test duplicate handling.
    rand_int = random.randint(1000, 9999)
    email = f"testuser{rand_int}@example.com"
    
    payload = {
        "email": "invalid-email",
        "password": "password123",
        "username": f"testuser{rand_int}",
        "role": "buyer"
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("SUCCESS: Signup successful.")
        else:
            print("FAILED: Signup failed.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_signup()
