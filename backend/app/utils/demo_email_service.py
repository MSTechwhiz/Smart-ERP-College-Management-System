import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

def send_demo_fee_email(student_name: str, student_email: str, amount: float, due_date: str) -> bool:
    """
    Sends a real demo fee reminder email to a specific student.
    Returns True if sent successfully, False otherwise.
    """
    try:
        # Load credentials from settings (loaded from .env)
        host = settings.email_host
        port = settings.email_port
        user = settings.email_user
        password = settings.email_password
        sender = getattr(settings, "email_from", user) # Fallback to user if email_from not in settings

        if not (host and port and user and password):
            logger.error("Demo Email: SMTP configuration is incomplete.")
            return False

        # Create message
        message = MIMEMultipart()
        message["From"] = sender
        message["To"] = student_email
        message["Subject"] = "Fee Payment Reminder – AcademiaOS"

        body = f"""Dear {student_name},

This is a fee reminder from AcademiaOS.

Your pending fee payment is due soon.

Student Name: {student_name}
Department: IT
Year: Final Year

Pending Amount: ₹{amount}
Due Date: {due_date}

Please complete the payment before the due date.

Regards
AcademiaOS Admin"""

        message.attach(MIMEText(body, "plain"))

        # Connect and send
        with smtplib.SMTP(host, port) as server:
            server.starttls() # Secure connection
            server.login(user, password)
            server.send_message(message)

        logger.info(f"Demo Email: Successfully sent to {student_email}")
        return True

    except Exception as e:
        logger.error(f"Demo Email Error: {str(e)}")
        return False
