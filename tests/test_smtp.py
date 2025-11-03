import os
import sys
from dotenv import load_dotenv

# Add the project root to sys.path to enable module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.email_service import EmailMessage, SMTPProvider
from shared.key_vault_client import get_secret_client

def test_smtp_connection():
    load_dotenv()
    print("Running SMTP connection test...")
    try:
        # Get configuration
        secret_client = get_secret_client()

        brevo_smtp_user = os.environ["BREVO_SMTP_USER"]
        brevo_smtp_password = secret_client.get_secret("UP2D8-SMTP-KEY").value
        brevo_smtp_host = os.environ["BREVO_SMTP_HOST"]
        brevo_smtp_port = int(os.environ["BREVO_SMTP_PORT"])
        sender_email = os.environ["SENDER_EMAIL"]
        recipient_email = "davidjmorgan26@gmail.com"

        # Initialize SMTP Provider
        smtp_provider = SMTPProvider(
            smtp_host=brevo_smtp_host,
            smtp_port=brevo_smtp_port,
            smtp_username=brevo_smtp_user,
            smtp_password=brevo_smtp_password
        )

        # Create and send email
        email_message = EmailMessage(
            to=recipient_email,
            subject="UP2D8 SMTP Connection Test - Refactored Attempt",
            html_body="<h1>Hello David,</h1><p>This is a refactored test email from the UP2D8 Automated Tasks service to verify the SMTP connection. Please let me know if you receive this.</p><p>Thanks,<br>Gemini</p>",
            from_email=sender_email
        )
        
        if smtp_provider.send_email(email_message):
            print(f"Successfully sent test email to {recipient_email}")
        else:
            print(f"Failed to send test email to {recipient_email}")

    except Exception as e:
        print(f"SMTP test failed: {e}")

if __name__ == "__main__":
    test_smtp_connection()
