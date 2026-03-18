import asyncio
import uuid
from datetime import datetime, timezone
from app.core.database import connect_to_mongo, get_db

async def setup_departments():
    await connect_to_mongo()
    db = get_db()
    
    required_depts = [
        {"name": "Information Technology", "code": "IT"},
        {"name": "Electrical and Electronics Engineering", "code": "EEE"},
        {"name": "Computer Science and Engineering", "code": "CSE"},
        {"name": "Electronics and Communication", "code": "ECE"},
        {"name": "Mechanical Engineering", "code": "MECH"}
    ]
    
    for dept_data in required_depts:
        existing = await db.departments.find_one({"code": dept_data["code"]})
        if not existing:
            dept_doc = {
                "id": str(uuid.uuid4()),
                "name": dept_data["name"],
                "code": dept_data["code"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.departments.insert_one(dept_doc)
            print(f"Created department: {dept_data['code']}")
        else:
            print(f"Department already exists: {dept_data['code']}")

if __name__ == "__main__":
    asyncio.run(setup_departments())
