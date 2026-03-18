import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

import logging
from dotenv import load_dotenv

# Setup logging to see Fast2SMS responses
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.utils.sms_service")

# Load .env
load_dotenv()

key = os.environ.get("FAST2SMS_API_KEY")
print(f"Loaded API Key: {key[:5]}...{key[-5:] if key else 'None'}")

# Set DB name for the session
os.environ["DB_NAME"] = "academia_erp"
os.environ["MONGO_URL"] = "mongodb://localhost:27017"

from app.core.database import get_db
from app.services.fee_notification_service import FeeNotificationService
from app.repositories.fee_repository import FeeRepository
from app.repositories.student_repository import StudentRepository

async def verify_activation():
    db = get_db()
    fee_repo = FeeRepository(db)
    student_repo = StudentRepository(db)
    service = FeeNotificationService(fee_repo, student_repo)
    
    # We expect this to call the real Fast2SMS API now
    print("Triggering REAL Fast2SMS notification for demo students...")
    results = await service.send_fee_reminders(manual=True)
    
    print(f"\nResults: {len(results)} students processed.")
    for r in results:
        print(f"- {r['student_name']} ({r.get('mobile')}): {r['fee_name']} - Status: {r['status']}")

if __name__ == "__main__":
    asyncio.run(verify_activation())
