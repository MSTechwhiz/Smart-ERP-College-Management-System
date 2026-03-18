import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
import uuid

async def setup_demo():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    # Change to academia_erp as per .env
    db = client["academia_erp"]
    
    # 1. Find Sanjay and Dhanush
    users = await db.users.find({"name": {"$regex": "Sanjay|Dhanush", "$options": "i"}}).to_list(None)
    print(f"Found {len(users)} users matching Sanjay/Dhanush in academia_erp")
    
    if not users:
        print("Demo students not found. Creating them...")
        # Create Sanjay
        sanjay_id = str(uuid.uuid4())
        await db.users.insert_one({
            "id": sanjay_id,
            "name": "Sanjay",
            "email": "sanjay@test.com",
            "role": "student",
            "is_active": True
        })
        await db.students.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": sanjay_id,
            "name": "Sanjay",
            "roll_number": "IT4001",
            "department_id": "IT",
            "batch": "2021-2025",
            "semester": 8,
            "is_active": True,
            "mobile_number": "9876543210"
        })
        # Create Dhanush
        dhanush_id = str(uuid.uuid4())
        await db.users.insert_one({
            "id": dhanush_id,
            "name": "Dhanush",
            "email": "dhanush@test.com",
            "role": "student",
            "is_active": True
        })
        await db.students.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": dhanush_id,
            "name": "Dhanush",
            "roll_number": "IT4002",
            "department_id": "IT",
            "batch": "2021-2025",
            "semester": 8,
            "is_active": True,
            "mobile_number": "9876543211"
        })
        users = await db.users.find({"name": {"$regex": "Sanjay|Dhanush", "$options": "i"}}).to_list(None)

    # 2. Create a Fee Structure due tomorrow
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
    fee_id = str(uuid.uuid4())
    fee_structure = {
        "id": fee_id,
        "name": "Final Year Verification Fee",
        "category": "semester",
        "amount": 15000,
        "due_date": tomorrow,
        "is_active": True
    }
    await db.fee_structures.insert_one(fee_structure)
    print(f"Created fee structure '{fee_structure['name']}' due on {tomorrow} in academia_erp")

    print("Verification setup complete.")
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_demo())
