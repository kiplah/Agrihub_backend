import requests

url = "http://127.0.0.1:8000/users/forgot_password/"
payload = {"email": "kiplahvictor27@gmail.com"}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    if response.status_code == 200:
        print("SUCCESS: Request with trailing slash worked.")
    else:
        print("FAILED: Request failed.")
except Exception as e:
    print(f"Error: {e}")
