import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_contact_us():
    print("\n--- Testing Contact Us ---")
    url = f"{BASE_URL}/api/contact-us/"
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "message": "This is a test message from the verification script."
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            print("SUCCESS: Contact Us message sent.")
        else:
            print("FAILED: Contact Us message failed.")
    except Exception as e:
        print(f"Error: {e}")

def test_product_filtering():
    print("\n--- Testing Product Filtering (Category=Seeds) ---")
    url = f"{BASE_URL}/products/?category=Seeds"
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        # print(f"Response: {response.text[:200]}...") # Truncate for brevity
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Retrieved {len(data)} products.")
            if len(data) > 0:
                print(f"Sample Product Category: {data[0].get('category_name')}")
        else:
            print("FAILED: Product filtering failed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_contact_us()
    test_product_filtering()
