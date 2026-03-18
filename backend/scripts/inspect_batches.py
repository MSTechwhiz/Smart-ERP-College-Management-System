import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def inspect_students():
    from app.core.database import connect_to_mongo, get_db
    await connect_to_mongo()
    db = get_db()
    
    print("--- Final Year Students (Year 4) ---")
    cursor = db.students.find({"year": {"$in": [4, "4"]}})
    students = await cursor.to_list(100)
    for s in students:
        print(f"ID: {s['id']}, Roll: {s.get('roll_number')}, Year: {s['year']}, Batch: {s.get('batch')}, DOB: {s.get('date_of_birth')}")

    print("\n--- All Students Batch Check ---")
    cursor = db.students.find({}, {"id": 1, "year": 1, "batch": 1, "admission_date": 1})
    all_students = await cursor.to_list(1000)
    for s in all_students:
        batch = s.get('batch', '')
        year = s.get('year')
        # If batch is 2021-2025 but year is 4... wait.
        # Let's just see them.
        pass

if __name__ == "__main__":
    asyncio.run(inspect_students())
