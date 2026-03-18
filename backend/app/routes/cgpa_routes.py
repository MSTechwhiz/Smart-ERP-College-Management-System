from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from ..core.security import get_current_user, require_roles
from ..services.cgpa_service import CGPAService, get_cgpa_service

router = APIRouter(prefix="/api/cgpa", tags=["CGPA Calculator"])

class CGPACalculateRequest(BaseModel):
    entries: List[dict]
    semester: Optional[int] = None
    save: bool = False

@router.post("/calculate-enhanced", response_model=dict)
async def calculate_cgpa_student(
    request: CGPACalculateRequest,
    user: dict = Depends(get_current_user),
    cgpa_service: CGPAService = Depends(get_cgpa_service)
):
    """Calculate SGPA/CGPA based on Anna University grading"""
    return await cgpa_service.calculate_enhanced(request.entries, request.semester, request.save, user)

@router.get("/history", response_model=List[dict])
async def get_cgpa_history(
    user: dict = Depends(get_current_user),
    cgpa_service: CGPAService = Depends(get_cgpa_service)
):
    """Get CGPA calculation history for student"""
    return await cgpa_service.get_history(user)

@router.get("/overall", response_model=dict)
async def get_overall_cgpa(
    user: dict = Depends(get_current_user),
    cgpa_service: CGPAService = Depends(get_cgpa_service)
):
    """Calculate overall CGPA from all semesters"""
    return await cgpa_service.get_overall_cgpa(user)


@router.post("/calculate", response_model=dict)
async def calculate_cgpa_manual(
    grades: List[dict],  # [{"credits": 4, "grade": "A+"}, ...]
    user: dict = Depends(get_current_user),
    cgpa_service: CGPAService = Depends(get_cgpa_service)
):
    """Manual CGPA calculator"""
    return cgpa_service.calculate_manual(grades)


@router.get("/recalculate/{student_id}", response_model=dict)
async def recalculate_student_cgpa(
    student_id: str,
    user: dict = Depends(require_roles(["principal", "admin", "hod"])),
    cgpa_service: CGPAService = Depends(get_cgpa_service)
):
    """Recalculate and update student CGPA"""
    return await cgpa_service.recalculate_student_cgpa(student_id)

