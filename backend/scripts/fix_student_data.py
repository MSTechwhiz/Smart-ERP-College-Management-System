import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def fix_student_data():
    from app.core.database import connect_to_mongo, get_db
    await connect_to_mongo()
    db = get_db()
    
    print("--- Correcting Final Year Batch (2021-2025 -> 2022-2026) ---")
    # Rule: Year 4 students should be 2022-2026 batch based on user request
    result = await db.students.update_many(
        {"year": {"$in": [4, "4"]}, "batch": "2021-2025"},
        {"$set": {"batch": "2022-2026"}}
    )
    print(f"Updated {result.modified_count} students to 2022-2026 batch.")

    print("\n--- Cleaning up Date of Birth fields ---")
    # Find DOBs with extra text (e.g., phone numbers attached)
    cursor = db.students.find({"date_of_birth": {"$regex": "\\s+"}})
    students_with_messy_dob = await cursor.to_list(1000)
    
    clean_count = 0
    for s in students_with_messy_dob:
        old_dob = s.get("date_of_birth", "")
        # Take the first part before space
        new_dob = old_dob.split()[0]
        if new_dob != old_dob:
            await db.students.update_one({"id": s["id"]}, {"$set": {"date_of_birth": new_dob}})
            clean_count += 1
            print(f"Cleaned DOB for {s.get('roll_number')}: '{old_dob}' -> '{new_dob}'")
            
    print(f"Cleaned up {clean_count} DOB fields.")

if __name__ == "__main__":
    asyncio.run(fix_student_data())
