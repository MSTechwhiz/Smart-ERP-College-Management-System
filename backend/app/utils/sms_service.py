import os
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SMSService:
    @staticmethod
    async def send_sms(to: str, message: str) -> bool:
        """
        Sends an SMS using Fast2SMS or Twilio based on env configuration.
        Returns True if sent successfully, False otherwise.
        """
        fast2sms_key = os.environ.get("FAST2SMS_API_KEY")
        twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        
        if fast2sms_key:
            return await SMSService._send_fast2sms(to, message, fast2sms_key)
        elif twilio_sid:
            return await SMSService._send_twilio(to, message)
        else:
            logger.error(f"No SMS Gateway configured. Failed to send message to {to}")
            return False

    @staticmethod
    async def _send_fast2sms(to: str, message: str, api_key: str) -> bool:
        url = "https://www.fast2sms.com/dev/bulkV2"
        headers = {
            "authorization": api_key,
            "Content-Type": "application/json"
        }
        
        # Standardize: Ensure numbers are 10 digits comma-separated as per user example
        raw_nums = to.split(",")
        clean_nums = []
        for n in raw_nums:
            c = n.strip()
            if c.startswith("91") and len(c) > 10: c = c[2:]
            clean_nums.append(c)
        numbers_str = ",".join(clean_nums)

        data = {
            "route": "q",
            "message": message,
            "language": "english",
            "flash": 0,
            "numbers": numbers_str
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=data, headers=headers)
                
                try:
                    result = response.json()
                    if result.get("return"):
                        logger.info(f"Fast2SMS: Message sent to {numbers_str}")
                        return True
                    else:
                        error_msg = result.get("message", "Unknown error")
                        logger.error(f"Fast2SMS Error: {error_msg}")
                        print(f"Fast2SMS API Error: {error_msg}")
                        return False
                except:
                    # If HTML error like "invalid format", it returns False
                    raw_err = response.text[:200]
                    logger.error(f"Fast2SMS returned non-JSON response: {raw_err}")
                    print(f"Fast2SMS Raw Error: {raw_err}")
                    return False
        except Exception as e:
            logger.error(f"Fast2SMS Exception: {e}")
            return False

    @staticmethod
    async def _send_twilio(to: str, message: str) -> bool:
        # Placeholder for Twilio integration if SID is found
        # (Requires twilio-python package, but httpx is enough for basic REST)
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_number = os.environ.get("TWILIO_FROM_NUMBER")
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        auth = (account_sid, auth_token)
        data = {
            "To": to if to.startswith("+") else f"+91{to}", # Assume India if no prefix
            "From": from_number,
            "Body": message
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=data, auth=auth)
                if response.status_code in [200, 201]:
                    logger.info(f"Twilio: Message sent to {to}")
                    return True
                else:
                    logger.error(f"Twilio Error: {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Twilio Exception: {e}")
            return False
