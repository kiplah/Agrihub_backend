import requests
import json

try:
    response = requests.get('http://127.0.0.1:8000/products/')
    data = response.json()
    
    # Print first product if exists
    if data and len(data) > 0:
        print(json.dumps(data[0], indent=2))
        if len(data) > 1:
            print("\nTotal products:", len(data))
    else:
        print("No products found in API response.")
except Exception as e:
    print(f"Error fetching: {e}")
