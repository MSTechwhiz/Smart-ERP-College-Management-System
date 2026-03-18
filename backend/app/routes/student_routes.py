from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import StreamingResponse
import bcrypt
import uuid
from datetime import datetime, timezone

from ..core.audit import log_audit
from ..core.database import get_db
from ..core.security import get_current_user, hash_password, require_roles
from ..schemas.auth_schema import User
from ..schemas.student_schema import Student, StudentCreate
from ..services.student_service import StudentService, get_student_service


router = APIRouter(prefix="/api/students", tags=["students"])


@router.post("", response_model=dict)
async def create_student(
    student_data: StudentCreate, 
    user: dict = Depends(require_roles(["principal", "admin"])),
    student_service: StudentService = Depends(get_student_service)
):
    student_dict = await student_service.create_student(student_data, user["id"])
    return {"message": "Student created", "student": student_dict}


@router.get("", response_model=dict)
async def get_students(
    department_id: Optional[str] = None,
    batch: Optional[str] = None,
    year: Optional[int] = None,
    semester: Optional[int] = None,
    section: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: Optional[int] = 100,
    user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(get_student_service)
):
    query: dict = {}

    if user["role"] == "hod":
        query["department_id"] = user["department_id"]
    elif user["role"] == "faculty":
        query["department_id"] = user["department_id"]
    elif user["role"] == "student":
        student = await student_service.student_repo.get_by_user_id(user["id"])
        if student:
            query["id"] = student["id"]

    if department_id and user["role"] in ["principal", "admin"]:
        query["department_id"] = department_id
    if batch:
        query["batch"] = batch
    if year:
        query["year"] = year
    if semester:
        query["semester"] = semester
    if section:
        query["section"] = section
    if category:
        query["admission_quota"] = category
    if search:
        query["search"] = search

    result = await student_service.get_students(query, skip=skip, limit=limit)
    return result


@router.get("/{student_id}", response_model=dict)
async def get_student_profile(
    student_id: str,
    user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(get_student_service)
):
    """Get student profile with authorization check"""
    # Use full profile service which already handles basic and linked data
    student_data = await student_service.get_student_full_profile(student_id, user)
    return student_data

@router.get("/{student_id}/admission-form")
async def get_admission_form(
    student_id: str,
    user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(get_student_service)
):
    # Authorization check
    if user["role"] not in ["admin", "principal"]:
        # Only students can access their own form
        if user["role"] == "student" and user["id"] != student_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this form")
    
    pdf_buffer = await student_service.get_admission_form_pdf(student_id, user)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=admission_form_{student_id}.pdf"}
    )


@router.put("/{student_id}", response_model=dict)
async def update_student(
    student_id: str,
    semester: Optional[int] = None,
    section: Optional[str] = None,
    mentor_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    user: dict = Depends(require_roles(["principal", "admin", "hod"])),
    student_service: StudentService = Depends(get_student_service)
):
    """Update student details"""
    student = await student_service.student_repo.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # HOD can only update students in their department
    if user["role"] == "hod" and student["department_id"] != user.get("department_id"):
        raise HTTPException(status_code=403, detail="Cannot update student from other department")

    update_data = {}
    if semester is not None:
        update_data["semester"] = semester
    if section is not None:
        update_data["section"] = section
    if mentor_id is not None:
        update_data["mentor_id"] = mentor_id
    if is_active is not None:
        update_data["is_active"] = is_active

    updated = await student_service.update_student(student_id, update_data, user["id"])
    return {"message": "Student updated", "student": updated}


@router.delete("/{student_id}", response_model=dict)
async def delete_student(
    student_id: str, 
    user: dict = Depends(require_roles(["principal", "admin"])),
    student_service: StudentService = Depends(get_student_service)
):
    """Delete student and user account"""
    await student_service.delete_student(student_id, user["id"])
    return {"message": "Student deleted"}


@router.get("/me/profile", response_model=dict)
async def get_my_student_profile(
    user: dict = Depends(require_roles(["student"])),
    student_service: StudentService = Depends(get_student_service)
):
    student = await student_service.get_my_student_profile(user)
    return student


@router.get("/{student_id}/full-profile", response_model=dict)
async def get_student_full_profile(
    student_id: str, 
    user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(get_student_service)
):
    """Get full student profile with documents"""
    return await student_service.get_student_full_profile(student_id, user)


@router.get("/{student_id}/documents", response_model=List[dict])
async def get_student_documents(
    student_id: str, 
    user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(get_student_service)
):
    """Get all documents for a student"""
    return await student_service.get_student_documents(student_id, user)


@router.post("/enhanced", response_model=dict)
async def create_enhanced_student(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    roll_number: Optional[str] = Form(None),
    department_id: str = Form(...),
    batch: str = Form(...),
    register_number: Optional[str] = Form(None),
    year: int = Form(1),
    semester: int = Form(1),
    section: Optional[str] = Form(None),
    date_of_birth: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    blood_group: Optional[str] = Form(None),
    mobile_number: Optional[str] = Form(None),
    alternate_mobile: Optional[str] = Form(None),
    program_type: Optional[str] = Form(None),
    program_duration: Optional[int] = Form(None),
    permanent_address: Optional[str] = Form(None),
    communication_address: Optional[str] = Form(None),
    tenth_school_name: Optional[str] = Form(None),
    tenth_board: Optional[str] = Form(None),
    tenth_year: Optional[int] = Form(None),
    tenth_total_marks: Optional[float] = Form(None),
    tenth_marks_obtained: Optional[float] = Form(None),
    tenth_percentage: Optional[float] = Form(None),
    twelfth_school_name: Optional[str] = Form(None),
    twelfth_board: Optional[str] = Form(None),
    twelfth_year: Optional[int] = Form(None),
    twelfth_total_marks: Optional[float] = Form(None),
    twelfth_marks_obtained: Optional[float] = Form(None),
    twelfth_percentage: Optional[float] = Form(None),
    twelfth_cutoff: Optional[float] = Form(None),
    id_type: Optional[str] = Form(None),
    id_number: Optional[str] = Form(None),
    community: Optional[str] = Form(None),
    scholarship_details: Optional[str] = Form(None),
    is_first_graduate: bool = Form(False),
    hostel_day_scholar: str = Form("day_scholar"),
    admission_type: Optional[str] = Form(None),
    father_name: Optional[str] = Form(None),
    father_occupation: Optional[str] = Form(None),
    father_contact: Optional[str] = Form(None),
    mother_name: Optional[str] = Form(None),
    mother_occupation: Optional[str] = Form(None),
    mother_contact: Optional[str] = Form(None),
    guardian_name: Optional[str] = Form(None),
    guardian_contact: Optional[str] = Form(None),
    regulation: str = Form("R2023"),
    mentor_id: Optional[str] = Form(None),
    user: dict = Depends(require_roles(["admin", "principal"])),
    student_service: StudentService = Depends(get_student_service)
):
    """Create student with enhanced profile"""
    params = {
        "name": name, "email": email, "password": password, "roll_number": roll_number,
        "department_id": department_id, "batch": batch, "register_number": register_number,
        "year": year, "semester": semester, "section": section, "date_of_birth": date_of_birth,
        "gender": gender, "blood_group": blood_group, "mobile_number": mobile_number,
        "alternate_mobile": alternate_mobile, "program_type": program_type,
        "program_duration": program_duration, "permanent_address": permanent_address,
        "communication_address": communication_address, "tenth_school_name": tenth_school_name,
        "tenth_board": tenth_board, "tenth_year": tenth_year, "tenth_total_marks": tenth_total_marks,
        "tenth_marks_obtained": tenth_marks_obtained, "tenth_percentage": tenth_percentage,
        "twelfth_school_name": twelfth_school_name, "twelfth_board": twelfth_board,
        "twelfth_year": twelfth_year, "twelfth_total_marks": twelfth_total_marks,
        "twelfth_marks_obtained": twelfth_marks_obtained, "twelfth_percentage": twelfth_percentage,
        "twelfth_cutoff": twelfth_cutoff, "id_type": id_type, "id_number": id_number,
        "community": community, "scholarship_details": scholarship_details,
        "is_first_graduate": is_first_graduate, "hostel_day_scholar": hostel_day_scholar,
        "admission_type": admission_type, "father_name": father_name, 
        "father_occupation": father_occupation, "father_contact": father_contact,
        "mother_name": mother_name, "mother_occupation": mother_occupation,
        "mother_contact": mother_contact, "guardian_name": guardian_name,
        "guardian_contact": guardian_contact, "regulation": regulation, "mentor_id": mentor_id
    }
    
    student_doc = await student_service.create_enhanced_student(params, user)
    return {"message": "Student created successfully", "student": student_doc}


@router.put("/{student_id}/profile", response_model=dict)
async def update_student_profile(
    student_id: str,
    register_number: Optional[str] = None,
    year: Optional[int] = None,
    semester: Optional[int] = None,
    section: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    gender: Optional[str] = None,
    blood_group: Optional[str] = None,
    mobile_number: Optional[str] = None,
    alternate_mobile: Optional[str] = None,
    program_type: Optional[str] = None,
    program_duration: Optional[int] = None,
    permanent_address: Optional[str] = None,
    communication_address: Optional[str] = None,
    community: Optional[str] = None,
    scholarship_details: Optional[str] = None,
    is_first_graduate: Optional[bool] = None,
    hostel_day_scholar: Optional[str] = None,
    admission_type: Optional[str] = None,
    father_name: Optional[str] = None,
    father_occupation: Optional[str] = None,
    father_contact: Optional[str] = None,
    mother_name: Optional[str] = None,
    mother_occupation: Optional[str] = None,
    mother_contact: Optional[str] = None,
    tenth_school_name: Optional[str] = None,
    tenth_board: Optional[str] = None,
    tenth_year: Optional[int] = None,
    tenth_total_marks: Optional[float] = None,
    tenth_marks_obtained: Optional[float] = None,
    tenth_percentage: Optional[float] = None,
    twelfth_school_name: Optional[str] = None,
    twelfth_board: Optional[str] = None,
    twelfth_year: Optional[int] = None,
    twelfth_total_marks: Optional[float] = None,
    twelfth_marks_obtained: Optional[float] = None,
    twelfth_percentage: Optional[float] = None,
    twelfth_cutoff: Optional[float] = None,
    id_type: Optional[str] = None,
    id_number: Optional[str] = None,
    user: dict = Depends(require_roles(["admin", "principal", "faculty"])),
    student_service: StudentService = Depends(get_student_service)
):
    """Update student profile"""
    fields_to_update = {
        "register_number": register_number, "year": year, "semester": semester,
        "section": section, "date_of_birth": date_of_birth, "gender": gender,
        "blood_group": blood_group, "mobile_number": mobile_number,
        "alternate_mobile": alternate_mobile, "permanent_address": permanent_address,
        "communication_address": communication_address, "community": community,
        "scholarship_details": scholarship_details, "hostel_day_scholar": hostel_day_scholar,
        "admission_type": admission_type,
        "tenth_school_name": tenth_school_name, "tenth_board": tenth_board, "tenth_year": tenth_year,
        "tenth_total_marks": tenth_total_marks, "tenth_marks_obtained": tenth_marks_obtained,
        "tenth_percentage": tenth_percentage,
        "twelfth_school_name": twelfth_school_name, "twelfth_board": twelfth_board, "twelfth_year": twelfth_year,
        "twelfth_total_marks": twelfth_total_marks, "twelfth_marks_obtained": twelfth_marks_obtained,
        "twelfth_percentage": twelfth_percentage, "twelfth_cutoff": twelfth_cutoff,
        "id_type": id_type, "id_number": id_number
    }
    
    parent_updates = {}
    if father_name: parent_updates["father_name"] = father_name
    if father_occupation: parent_updates["father_occupation"] = father_occupation
    if father_contact: parent_updates["father_contact"] = father_contact
    if mother_name: parent_updates["mother_name"] = mother_name
    if mother_occupation: parent_updates["mother_occupation"] = mother_occupation
    if mother_contact: parent_updates["mother_contact"] = mother_contact

    updated = await student_service.update_student_profile(
        student_id, fields_to_update, is_first_graduate, parent_updates, user
    )
    
    return {"message": "Profile updated successfully", "student": updated}
