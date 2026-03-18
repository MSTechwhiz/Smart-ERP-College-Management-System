import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def debug_timetable(email):
    MONGODB_URL = "mongodb://localhost:27017"
    DATABASE_NAME = "academia_erp"
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    print(f"Checking user: {email}")
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        print("User not found in 'users' collection.")
        return
        
    print(f"User ID: {user['id']}, Role: {user['role']}")
    
    # Check student profile
    student = await db.students.find_one({"user_id": user["id"]})
    if not student:
        print("Student profile NOT found in 'students' collection!")
        # Check if it's stored with 'id' instead of 'user_id' or something
        student_by_id = await db.students.find_one({"id": user["id"]})
        if student_by_id:
            print("Found student by 'id' field instead of 'user_id'.")
            student = student_by_id
        else:
            print("Totally missing from 'students' collection.")
            return

    print(f"Student Profile: Semester={student.get('semester')}, Section={student.get('section')}, DeptID={student.get('department_id')}")
    
    # Simulate service logic
    query = {
        "semester": student.get("semester"),
        "section": student.get("section")
    }
    dept_id = student.get("department_id")
    
    print(f"Querying mappings with: {query}, dept_id={dept_id}")
    
    # Manual mapping fetch
    subject_ids = []
    if dept_id:
        subjects = await db.subjects.find({"department_id": dept_id}).to_list(None)
        subject_ids = [s["id"] for s in subjects]
        print(f"Found {len(subject_ids)} subjects for department {dept_id}")
        if subject_ids:
            query["subject_id"] = {"$in": subject_ids}
    
    mappings = await db.subject_faculty_mappings.find(query).to_list(None)
    print(f"Found {len(mappings)} mappings.")
    
    for m in mappings:
        print(f"  Day: {m.get('day')}, Period: {m.get('period')}, Subject: {m.get('subject_id')}")

if __name__ == "__main__":
    asyncio.run(debug_timetable("aagalya236@gmail.com"))
