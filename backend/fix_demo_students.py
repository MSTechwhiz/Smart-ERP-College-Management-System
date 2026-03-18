import asyncio
import motor.motor_asyncio
import uuid

async def fix_demo_students():
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["academia_erp"]
    
    # Target Data
    demo_data = [
        {
            "name": "Sanjay M",
            "roll": "IT4001",
            "mobile": "8667781655",
            "email": "sanjay.m@test.com"
        },
        {
            "name": "J Dhanush",
            "roll": "IT4002",
            "mobile": "8838216441",
            "email": "jdhanush@test.com"
        }
    ]
    
    for data in demo_data:
        # Check by roll number (safe identifier in my previous setup)
        student = await db.students.find_one({"roll_number": data["roll"]})
        if student:
            print(f"Updating student {data['roll']}...")
            await db.students.update_one(
                {"id": student["id"]},
                {"$set": {
                    "name": data["name"],
                    "mobile_number": data["mobile"],
                    "department_id": "IT",
                    "batch": "2021-2025", # Final Year
                    "semester": 8
                }}
            )
            # Update associated user name
            await db.users.update_one(
                {"id": student["user_id"]},
                {"$set": {"name": data["name"]}}
            )
        else:
            print(f"Creating student {data['roll']}...")
            user_id = str(uuid.uuid4())
            await db.users.insert_one({
                "id": user_id,
                "name": data["name"],
                "email": data["email"],
                "role": "student",
                "is_active": True
            })
            await db.students.insert_one({
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": data["name"],
                "roll_number": data["roll"],
                "department_id": "IT",
                "batch": "2021-2025",
                "semester": 8,
                "is_active": True,
                "mobile_number": data["mobile"]
            })

    # Also create the fee structure if it doesn't exist (due tomorrow)
    from datetime import datetime, timezone, timedelta
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
    
    existing_fee = await db.fee_structures.find_one({"name": "Final Year Verification Fee"})
    if not existing_fee:
        await db.fee_structures.insert_one({
            "id": str(uuid.uuid4()),
            "name": "Final Year Verification Fee",
            "category": "semester",
            "amount": 15000,
            "due_date": tomorrow,
            "is_active": True,
            "department_id": "IT",
            "batch": "2021-2025"
        })
    else:
        await db.fee_structures.update_one(
            {"id": existing_fee["id"]},
            {"$set": {"due_date": tomorrow, "is_active": True}}
        )

    print("Demo setup updated successfully.")
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_demo_students())
