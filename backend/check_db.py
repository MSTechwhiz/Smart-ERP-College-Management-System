import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def run():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.college_erp
    
    s_count = await db.students.count_documents({})
    d_count = await db.departments.count_documents({})
    u_count = await db.users.count_documents({})
    
    print(f"Students: {s_count}")
    print(f"Departments: {d_count}")
    print(f"Users: {u_count}")
    
    if s_count == 0:
        print("No students found. Seed might have failed or data was cleared.")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(run())
