import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_timetable_service(email):
    from app.core.database import connect_to_mongo, get_db
    from app.services.subject_service import get_subject_service
    from app.repositories.student_repository import get_student_repository
    
    await connect_to_mongo()
    db = get_db()
    
    student_repo = get_student_repository(db)
    subject_service = get_subject_service() # Need to pass repo or get from Depends
    # Manual setup since it's not a request
    from app.repositories.subject_repository import get_subject_repository
    subject_repo = get_subject_repository(db)
    from app.services.subject_service import SubjectService
    service = SubjectService(subject_repo)
    
    print(f"Testing for student: {email}")
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        print("User not found")
        return
        
    student = await student_repo.get_by_user_id(user["id"])
    if not student:
        print("Student not found")
        return
        
    print(f"Calling service.get_student_timetable...")
    try:
        result = await service.get_student_timetable(student)
        print(f"Result length: {len(result)}")
        import json
        print(f"Result JSON: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"CRITICAL ERROR in Service:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_timetable_service("aagalya236@gmail.com"))
