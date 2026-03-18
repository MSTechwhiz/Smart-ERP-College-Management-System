import os
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class WhatsAppService:
    @staticmethod
    async def send_whatsapp(to: str, message: str) -> bool:
        """
        Sends a WhatsApp message using CallMeBot or Twilio based on env configuration.
        Returns True if sent successfully, False otherwise.
        """
        whatsapp_key = os.environ.get("WHATSAPP_API_KEY") # CallMeBot API Key
        twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        
        # Format phone number for international (assuming India if 10 digits)
        clean_number = to.strip()
        if len(clean_number) == 10:
            clean_number = f"91{clean_number}"
        
        if whatsapp_key:
            return await WhatsAppService._send_callmebot(clean_number, message, whatsapp_key)
        elif twilio_sid and os.environ.get("TWILIO_WHATSAPP_FROM"):
            return await WhatsAppService._send_twilio_whatsapp(clean_number, message)
        else:
            logger.error(f"No WhatsApp Gateway configured. Failed to send message to {to}")
            return False

    @staticmethod
    async def _send_callmebot(to: str, message: str, api_key: str) -> bool:
        """
        CallMeBot WhatsApp API
        Endpoint: https://api.callmebot.com/whatsapp.php?phone=[phone]&text=[message]&apikey=[apikey]
        """
        url = "https://api.callmebot.com/whatsapp.php"
        params = {
            "phone": to,
            "text": message,
            "apikey": api_key
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # CallMeBot often uses GET for simple text
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    logger.info(f"CallMeBot: WhatsApp message sent to {to}")
                    return True
                else:
                    logger.error(f"CallMeBot Error: {response.text}")
                    return False
        except Exception as e:
            logger.error(f"CallMeBot Exception: {e}")
            return False

    @staticmethod
    async def _send_twilio_whatsapp(to: str, message: str) -> bool:
        """
        Twilio WhatsApp API
        """
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_whatsapp = os.environ.get("TWILIO_WHATSAPP_FROM") # e.g., whatsapp:+14155238886
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        auth = (account_sid, auth_token)
        
        target = f"whatsapp:+{to}" if not to.startswith("whatsapp:") else to
        
        data = {
            "To": target,
            "From": from_whatsapp,
            "Body": message
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=data, auth=auth)
                if response.status_code in [200, 201]:
                    logger.info(f"Twilio WhatsApp: Message sent to {to}")
                    return True
                else:
                    logger.error(f"Twilio WhatsApp Error: {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Twilio WhatsApp Exception: {e}")
            return False
