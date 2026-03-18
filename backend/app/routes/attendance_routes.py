from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from ..core.security import get_current_user, require_roles
from ..schemas.attendance_schema import Attendance, AttendanceCreate, BulkAttendanceCreate
from ..services.attendance_service import AttendanceService, get_attendance_service
from ..services.student_service import StudentService, get_student_service

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])

@router.post("", response_model=dict)
async def mark_attendance(
    attendance_data: AttendanceCreate,
    user: dict = Depends(require_roles(["faculty", "admin"])),
    attendance_service: AttendanceService = Depends(get_attendance_service)
):
    doc = await attendance_service.mark_attendance(attendance_data, user["id"])
    return {"message": "Attendance marked", "attendance": doc}

@router.post("/bulk", response_model=dict)
async def mark_bulk_attendance(
    bulk_data: BulkAttendanceCreate,
    user: dict = Depends(require_roles(["faculty", "admin"])),
    attendance_service: AttendanceService = Depends(get_attendance_service)
):
    result = await attendance_service.mark_bulk_attendance(bulk_data, user["id"])
    return {"message": result["message"]}

@router.get("", response_model=List[dict])
async def get_attendance(
    student_id: Optional[str] = None,
    subject_id: Optional[str] = None,
    date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    user: dict = Depends(get_current_user),
    attendance_service: AttendanceService = Depends(get_attendance_service),
    student_service: StudentService = Depends(get_student_service)
):
    query = {}
    
    if user["role"] == "student":
        student = await student_service.student_repo.get_by_user_id(user["id"])
        if student:
            query["student_id"] = student["id"]
    elif student_id:
        query["student_id"] = student_id
    
    if subject_id:
        query["subject_id"] = subject_id
    if date:
        query["date"] = date
    
    attendance = await attendance_service.get_attendance(query, skip=skip, limit=limit)
    return attendance

@router.get("/summary/{student_id}", response_model=dict)
async def get_attendance_summary(
    student_id: str, 
    skip: int = 0,
    limit: int = 100,
    user: dict = Depends(get_current_user),
    attendance_service: AttendanceService = Depends(get_attendance_service),
    student_service: StudentService = Depends(get_student_service)
):
    # Permission check
    if user["role"] == "student":
        student = await student_service.student_repo.get_by_user_id(user["id"])
        if not student or student["id"] != student_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    summary = await attendance_service.get_summary(student_id, skip=skip, limit=limit)
    return {"student_id": student_id, "summary": summary}
