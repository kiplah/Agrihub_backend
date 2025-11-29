import os
import requests
import json
from django.template.loader import render_to_string
from django.conf import settings

class EmailService:
    @staticmethod
    def _send_email(to_email, subject, html_content):
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
                    "email": to_email
                }
            ],
            "subject": subject,
            "htmlContent": html_content
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

    @staticmethod
    def send_verification_email(user, code):
        subject = "AgroMart Email Verification"
        context = {
            'username': user.username,
            'code': code
        }
        html_content = render_to_string('emails/verification.html', context)
        return EmailService._send_email(user.email, subject, html_content)

    @staticmethod
    def send_password_reset_email(user, code):
        subject = "AgroMart Password Reset"
        context = {
            'username': user.username,
            'code': code
        }
        html_content = render_to_string('emails/reset_password.html', context)
        return EmailService._send_email(user.email, subject, html_content)
