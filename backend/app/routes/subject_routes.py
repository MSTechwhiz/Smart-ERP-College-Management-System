from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from ..core.database import get_db
from ..core.security import get_current_user, require_roles
from ..core.audit import log_audit
from ..schemas.subject_schema import Subject, SubjectCreate, SubjectFacultyMapping, SubjectFacultyMappingCreate
from ..services.subject_service import SubjectService, get_subject_service

router = APIRouter(prefix="/api/subjects", tags=["Subjects"])

@router.post("", response_model=dict)
async def create_subject(
    subject_data: SubjectCreate, 
    user: dict = Depends(require_roles(["principal", "admin", "hod"])),
    subject_service: SubjectService = Depends(get_subject_service)
):
    doc = await subject_service.create_subject(subject_data, user["id"])
    return {"message": "Subject created", "subject": doc}

@router.get("", response_model=List[dict])
async def get_subjects(
    department_id: Optional[str] = None,
    semester: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    user: dict = Depends(get_current_user),
    subject_service: SubjectService = Depends(get_subject_service)
):
    query = {}
    if department_id:
        query["department_id"] = department_id
    if semester:
        query["semester"] = semester
    
    return await subject_service.get_subjects(query, skip=skip, limit=limit)

@router.post("/mapping", response_model=dict)
async def create_subject_faculty_mapping(
    mapping_data: SubjectFacultyMappingCreate,
    user: dict = Depends(require_roles(["principal", "admin", "hod"])),
    subject_service: SubjectService = Depends(get_subject_service)
):
    doc = await subject_service.create_mapping(mapping_data.model_dump())
    return {"message": "Subject-faculty mapping created", "mapping": doc}

@router.get("/mappings", response_model=List[dict])
async def get_subject_faculty_mappings(
    faculty_id: Optional[str] = None,
    academic_year: Optional[str] = None,
    semester: Optional[int] = None,
    section: Optional[str] = None,
    department_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    user: dict = Depends(get_current_user),
    subject_service: SubjectService = Depends(get_subject_service)
):
    query = {}
    if faculty_id:
        # If the frontend passes user.id (which it does in Faculty dashboard),
        # we need to resolve it to the faculty collection ID.
        from ..core.database import get_db
        db = get_db()
        faculty_profile = await db.faculty.find_one({"user_id": faculty_id})
        if faculty_profile:
            query["faculty_id"] = faculty_profile["id"]
        else:
            query["faculty_id"] = faculty_id
            
    if academic_year:
        query["academic_year"] = academic_year
    if semester:
        query["semester"] = semester
    if section:
        query["section"] = section
    
    return await subject_service.get_mappings(query, department_id=department_id, skip=skip, limit=limit)

@router.get("/student-timetable", response_model=List[dict])
async def get_student_timetable(
    user: dict = Depends(require_roles(["student"])),
    subject_service: SubjectService = Depends(get_subject_service)
):
    from ..repositories.student_repository import get_student_repository
    from ..core.database import get_db
    db = get_db()
    student_repo = get_student_repository(db)
    
    student = await student_repo.get_by_user_id(user["id"])
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    return await subject_service.get_student_timetable(student)

@router.put("/{subject_id}", response_model=dict)
async def update_subject(
    subject_id: str,
    name: Optional[str] = None,
    credits: Optional[int] = None,
    subject_type: Optional[str] = None,
    user: dict = Depends(require_roles(["principal", "admin", "hod"])),
    subject_service: SubjectService = Depends(get_subject_service)
):
    update_data = {}
    if name: update_data["name"] = name
    if credits: update_data["credits"] = credits
    if subject_type: update_data["subject_type"] = subject_type
    
    updated = await subject_service.update_subject(subject_id, update_data)
    return {"message": "Subject updated", "subject": updated}

@router.delete("/{subject_id}", response_model=dict)
async def delete_subject(
    subject_id: str, 
    user: dict = Depends(require_roles(["principal", "admin", "hod"])),
    subject_service: SubjectService = Depends(get_subject_service)
):
    await subject_service.delete_subject(subject_id)
    return {"message": "Subject deleted"}
