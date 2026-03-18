import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import bcrypt

async def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

async def run():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.college_erp
    
    # Get CSE department ID
    dept = await db.departments.find_one({"code": "CSE"})
    if not dept:
        print("CSE Department not found")
        return
    
    # Get Faculty ID for mentor
    faculty = await db.faculty.find_one({"employee_id": "FAC001"})
    mentor_id = faculty["id"] if faculty else None

    user_id = "00000000-0000-0000-0000-000000000001" # Consistent ID if possible
    
    # Create User
    user_doc = {
        "id": user_id,
        "email": "student@academia.edu",
        "name": "Rahul Verma",
        "password": await hash_password("student123"),
        "role": "student",
        "department_id": dept["id"],
        "permissions": [],
        "sub_roles": [],
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Create Student
    student_doc = {
        "id": "11111111-1111-1111-1111-111111111111",
        "user_id": user_id,
        "roll_number": "21CSE001",
        "department_id": dept["id"],
        "batch": "2021-2025",
        "semester": 5,
        "section": "A",
        "mentor_id": mentor_id,
        "cgpa": 8.5,
        "is_active": True,
        "admission_date": datetime.now(timezone.utc).isoformat()
    }
    
    # Clean existing if any (shouldn't be there based on count but safer)
    await db.users.delete_one({"email": "student@academia.edu"})
    await db.students.delete_one({"roll_number": "21CSE001"})
    
    await db.users.insert_one(user_doc)
    await db.students.insert_one(student_doc)
    
    print("Rahul Verma restored successfully.")
    client.close()

if __name__ == "__main__":
    asyncio.run(run())
