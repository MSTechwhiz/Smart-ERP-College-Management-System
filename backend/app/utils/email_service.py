import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from ..core.config import get_settings

logger = logging.getLogger(__name__)

def send_email_notification(to_email: str, subject: str, message: str) -> bool:
    """
    Sends an email notification using SMTP.
    Returns True if success, False otherwise.
    """
    settings = get_settings()
    
    # Validation
    if not settings.email_host or not settings.email_user or not settings.email_password:
        logger.warning("SMTP settings are not configured. Skipping email.")
        return False
        
    if not to_email or "@" not in to_email:
        logger.warning(f"Invalid email address: {to_email}")
        return False

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = settings.email_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect and send
        with smtplib.SMTP(settings.email_host, settings.email_port) as server:
            server.starttls() # Secure TLS
            server.login(settings.email_user, settings.email_password)
            server.send_message(msg)
            
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False
