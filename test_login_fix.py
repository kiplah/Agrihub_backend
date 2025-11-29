import requests

url = "http://127.0.0.1:8000/login/"
payload = {
    "email": "kiplahvictor27@gmail.com",
    "password": "newpassword456" # Assuming this was set in previous steps
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    if response.status_code == 200:
        print("SUCCESS: Login with trailing slash worked.")
    else:
        print("FAILED: Login failed.")
except Exception as e:
    print(f"Error: {e}")
