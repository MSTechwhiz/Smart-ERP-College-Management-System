import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Set DB name for the session if needed
os.environ["DB_NAME"] = "academia_erp"
os.environ["MONGO_URL"] = "mongodb://localhost:27017"

from app.core.database import get_db
from app.services.fee_notification_service import FeeNotificationService
from app.repositories.fee_repository import FeeRepository
from app.repositories.student_repository import StudentRepository

async def run_internal_test():
    db = get_db()
    fee_repo = FeeRepository(db)
    student_repo = StudentRepository(db)
    service = FeeNotificationService(fee_repo, student_repo)
    
    print("Running fee reminders internal check (DEMO MODE / MANUAL)...")
    results = await service.send_fee_reminders(manual=True)
    
    print(f"Results: {len(results)} students notified.")
    for r in results:
        print(f"- {r['student_name']} ({r.get('mobile', 'No Mobile')}): {r['fee_name']} - {r['status']}")

if __name__ == "__main__":
    asyncio.run(run_internal_test())
