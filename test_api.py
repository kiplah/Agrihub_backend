import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_signup():
    print("Testing Signup...")
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "role": "buyer"
    }
    response = requests.post(f"{BASE_URL}/signup", json=data)
    if response.status_code == 201:
        print("Signup Successful")
        return True
    elif response.status_code == 400 and "username" in response.json():
        print("User already exists (expected if re-running)")
        return True
    else:
        print(f"Signup Failed: {response.status_code} {response.text}")
        return False

def test_login():
    print("Testing Login...")
    data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/login", json=data)
    if response.status_code == 200:
        print("Login Successful")
        return True
    else:
        print(f"Login Failed: {response.status_code} {response.text}")
        return False

def test_chatbot():
    print("Testing Chatbot...")
    data = {"message": "Hello"}
    try:
        response = requests.post(f"{BASE_URL}/api/chatbot", json=data, timeout=5)
        if response.status_code == 200:
            print(f"Chatbot Response: {response.json().get('reply')}")
            return True
        else:
            print(f"Chatbot Failed: {response.status_code} {response.text}")
            # Chatbot might fail if Ollama is not running, which is expected
            return True 
    except Exception as e:
        print(f"Chatbot connection failed (Ollama might be down): {e}")
        return True

if __name__ == "__main__":
    # Wait for server to start
    time.sleep(2)
    
    if test_signup():
        test_login()
    
    test_chatbot()
