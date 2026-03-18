from __future__ import annotations
from fastapi import APIRouter, HTTPException
from ..core.database import get_db
from ..core.security import hash_password
from ..schemas.auth_schema import User
from ..schemas.student_schema import Student
from ..schemas.faculty_schema import Faculty
from ..schemas.department_schema import Department
from ..schemas.subject_schema import Subject
from ..schemas.fee_schema import FeeStructure
from ..schemas.announcement_schema import Announcement
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api", tags=["Seed Data"])

@router.post("/seed", response_model=dict)
async def seed_demo_data():
    print("Seed started")
    db = get_db()
    
    # Verify connection first
    try:
        await db.command("ping")
        print("Database connected")
    except Exception as e:
        print(f"Database connection failed: {e}")
        return {"status": "error", "message": f"Database connection failed: {str(e)}"}
    
    """Seed demo data for testing"""
    
    # Check if data already exists - check students collection specifically
    student_count = await db.students.count_documents({})
    if student_count > 0:
        print("Seed skipped: Database already contains student records")
        return {"status": "already_seeded", "message": "Database already contains records"}
    
    # Create departments
    departments_data = [
        {"name": "Computer Science and Engineering", "code": "CSE"},
        {"name": "Electronics and Communication", "code": "ECE"},
        {"name": "Mechanical Engineering", "code": "MECH"}
    ]
    
    dept_ids = {}
    dept_docs = []
    for dept_data in departments_data:
        dept = Department(**dept_data)
        doc = dept.model_dump()
        doc["created_at"] = doc["created_at"].isoformat()
        dept_docs.append(doc)
        dept_ids[dept_data["code"]] = dept.id
        
    if dept_docs:
        await db.departments.insert_many(dept_docs)
    
    # Create Principal
    principal_user = User(
        email="principal@academia.edu",
        name="Dr Rajesh Kumar",
        role="principal",
        permissions=["all"]
    )
    principal_dict = principal_user.model_dump()
    principal_dict["password"] = await hash_password("principal123")
    principal_dict["created_at"] = principal_dict["created_at"].isoformat()
    await db.users.insert_one(principal_dict)
    
    # Create Admin
    admin_user = User(
        email="admin@academia.edu",
        name="Admin User",
        role="admin",
        permissions=["manage_students", "manage_faculty", "manage_fees"]
    )
    admin_dict = admin_user.model_dump()
    admin_dict["password"] = await hash_password("admin123")
    admin_dict["created_at"] = admin_dict["created_at"].isoformat()
    await db.users.insert_one(admin_dict)
    
    # Create HOD for CSE
    hod_user = User(
        email="hod.cse@academia.edu",
        name="Dr Priya Sharma",
        role="hod",
        department_id=dept_ids["CSE"],
        permissions=["manage_department"]
    )
    hod_dict = hod_user.model_dump()
    hod_dict["password"] = await hash_password("hod123")
    hod_dict["created_at"] = hod_dict["created_at"].isoformat()
    await db.users.insert_one(hod_dict)
    
    # Update department with HOD
    await db.departments.update_one({"id": dept_ids["CSE"]}, {"$set": {"hod_id": hod_user.id}})
    
    # Create Faculty
    faculty_user = User(
        email="faculty@academia.edu",
        name="Prof Amit Singh",
        role="faculty",
        department_id=dept_ids["CSE"],
        sub_roles=["class_incharge"]
    )
    faculty_dict = faculty_user.model_dump()
    faculty_dict["password"] = await hash_password("faculty123")
    faculty_dict["created_at"] = faculty_dict["created_at"].isoformat()
    await db.users.insert_one(faculty_dict)
    
    faculty = Faculty(
        user_id=faculty_user.id,
        employee_id="FAC001",
        department_id=dept_ids["CSE"],
        designation="Assistant Professor",
        specialization="Machine Learning",
        is_class_incharge=True,
        incharge_class="CSE-A-3"
    )
    faculty_profile = faculty.model_dump()
    faculty_profile["joining_date"] = faculty_profile["joining_date"].isoformat()
    await db.faculty.insert_one(faculty_profile)
    
    # Create Student
    student_user = User(
        email="student@academia.edu",
        name="Rahul Verma",
        role="student",
        department_id=dept_ids["CSE"]
    )
    student_dict = student_user.model_dump()
    student_dict["password"] = await hash_password("student123")
    student_dict["created_at"] = student_dict["created_at"].isoformat()
    await db.users.insert_one(student_dict)
    
    student = Student(
        user_id=student_user.id,
        roll_number="21CSE001",
        department_id=dept_ids["CSE"],
        batch="2021-2025",
        semester=5,
        section="A",
        mentor_id=faculty.id,
        cgpa=8.5
    )
    student_profile = student.model_dump()
    student_profile["admission_date"] = student_profile["admission_date"].isoformat()
    await db.students.insert_one(student_profile)
    
    # Create Subjects
    subjects_data = [
        {"code": "CS501", "name": "Machine Learning", "department_id": dept_ids["CSE"], "semester": 5, "credits": 4, "subject_type": "theory"},
        {"code": "CS502", "name": "Data Structures", "department_id": dept_ids["CSE"], "semester": 5, "credits": 3, "subject_type": "theory"},
        {"code": "CS503", "name": "Database Management", "department_id": dept_ids["CSE"], "semester": 5, "credits": 4, "subject_type": "theory"},
        {"code": "CS504L", "name": "ML Lab", "department_id": dept_ids["CSE"], "semester": 5, "credits": 2, "subject_type": "lab"}
    ]
    
    subject_docs = []
    for subj_data in subjects_data:
        subject = Subject(**subj_data)
        subject_docs.append(subject.model_dump())
        
    if subject_docs:
        await db.subjects.insert_many(subject_docs)
    
    # Create Fee Structure
    fee_structures = [
        {"name": "Tuition Fee - Semester 5", "category": "tuition", "amount": 75000, "semester": 5},
        {"name": "Exam Fee - Semester 5", "category": "exam", "amount": 3000, "semester": 5},
        {"name": "Lab Fee", "category": "misc", "amount": 5000, "semester": 5}
    ]
    
    fee_docs = []
    for fee_data in fee_structures:
        fee = FeeStructure(**fee_data)
        fee_docs.append(fee.model_dump())
        
    if fee_docs:
        await db.fee_structures.insert_many(fee_docs)
    
    # Create sample announcement
    announcement = Announcement(
        title="Welcome to New Academic Session",
        content="Dear Students, Welcome to the new academic session 2024-25. Classes will begin from January 15th. All students are requested to complete their fee payment before the due date.",
        created_by=principal_user.id,
        target_roles=["student", "faculty"]
    )
    ann_dict = announcement.model_dump()
    ann_dict["publish_date"] = ann_dict["publish_date"].isoformat()
    await db.announcements.insert_one(ann_dict)
    
    return {
        "message": "Demo data seeded successfully",
        "credentials": {
            "principal": {"email": "principal@academia.edu", "password": "principal123"},
            "admin": {"email": "admin@academia.edu", "password": "admin123"},
            "hod": {"email": "hod.cse@academia.edu", "password": "hod123"},
            "faculty": {"email": "faculty@academia.edu", "password": "faculty123"},
            "student": {"email": "student@academia.edu", "password": "student123"}
        }
    }
