from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from ..core.security import get_current_user, require_roles
from ..schemas.marks_schema import Marks, MarksCreate, BulkMarksCreate
from ..services.marks_service import MarksService, get_marks_service
from ..services.student_service import StudentService, get_student_service

router = APIRouter(prefix="/api/marks", tags=["Marks"])

@router.post("", response_model=dict)
async def enter_marks(
    marks_data: MarksCreate,
    user: dict = Depends(require_roles(["faculty", "admin"])),
    marks_service: MarksService = Depends(get_marks_service)
):
    doc = await marks_service.enter_marks(marks_data, user["id"], user["name"], user["role"])
    return {"message": "Marks entered", "marks": doc}

@router.post("/bulk", response_model=dict)
async def enter_bulk_marks(
    bulk_data: BulkMarksCreate,
    user: dict = Depends(require_roles(["faculty", "admin"])),
    marks_service: MarksService = Depends(get_marks_service)
):
    result = await marks_service.enter_bulk_marks(bulk_data, user["id"])
    return {"message": result["message"]}

@router.get("", response_model=List[dict])
async def get_marks(
    student_id: Optional[str] = None,
    department_id: Optional[str] = None,
    subject_id: Optional[str] = None,
    academic_year: Optional[str] = None,
    semester: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    user: dict = Depends(get_current_user),
    marks_service: MarksService = Depends(get_marks_service),
    student_service: StudentService = Depends(get_student_service)
):
    query = {}
    
    if user["role"] == "faculty":
        # Faculty can only see their department's marks
        query["department_id"] = user["department_id"]
    elif user["role"] == "student":
        student = await student_service.student_repo.get_by_user_id(user["id"])
        if student:
            query["student_id"] = student["id"]
    elif student_id:
        query["student_id"] = student_id
    
    if department_id and user["role"] in ["principal", "admin", "hod"]:
        query["department_id"] = department_id
    
    if subject_id:
        query["subject_id"] = subject_id
    if academic_year:
        query["academic_year"] = academic_year
    if semester:
        query["semester"] = semester
    
    marks = await marks_service.get_marks(query, skip=skip, limit=limit)
    return marks

@router.put("/{marks_id}/lock", response_model=dict)
async def lock_marks(
    marks_id: str, 
    user: dict = Depends(require_roles(["principal", "hod"])),
    marks_service: MarksService = Depends(get_marks_service)
):
    doc = await marks_service.lock_marks(marks_id, user["id"], user["name"], user["role"])
    return {"message": "Marks locked", "marks": doc}

@router.get("/cgpa/{student_id}", response_model=dict)
async def get_student_cgpa(
    student_id: str, 
    user: dict = Depends(get_current_user),
    marks_service: MarksService = Depends(get_marks_service),
    student_service: StudentService = Depends(get_student_service)
):
    # Permission check
    if user["role"] == "student":
        student = await student_service.student_repo.get_by_user_id(user["id"])
        if not student or student["id"] != student_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    result = await marks_service.get_cgpa_data(student_id)
    return result
