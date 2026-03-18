import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def inspect_mappings():
    MONGODB_URL = "mongodb://localhost:27017"
    DATABASE_NAME = "academia_erp"
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    print("All Mappings in 'subject_faculty_mappings':")
    mappings = await db.subject_faculty_mappings.find().to_list(None)
    for m in mappings:
        subject = await db.subjects.find_one({"id": m.get("subject_id")})
        s_name = subject.get("name") if subject else "Unknown"
        print(f"Subject: {s_name}, Sem: {m.get('semester')}, Sec: {m.get('section')}, Year: {m.get('academic_year')}, Day: {m.get('day')}, Period: {m.get('period')}")

if __name__ == "__main__":
    asyncio.run(inspect_mappings())
