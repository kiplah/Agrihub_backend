import os
import requests
import json

def send_verification_email(email, code):
    api_key = os.getenv("BREVO_API_KEY")
    from_email = os.getenv("BREVO_FROM_EMAIL")
    from_name = os.getenv("BREVO_FROM_NAME")

    url = "https://api.brevo.com/v3/smtp/email"
    
    payload = {
        "sender": {
            "name": from_name,
            "email": from_email
        },
        "to": [
            {
                "email": email
            }
        ],
        "subject": "AgroMart Email Verification",
        "htmlContent": f"""
            <h2>Welcome to AgroMart!</h2>
            <p>Your verification code is: <strong>{code}</strong></p>
            <p>Please enter this code to complete your registration.</p>
        """
    }

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        if response.status_code == 201:
            return True, None
        else:
            return False, f"Failed to send email, status: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return False, str(e)
