from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from ..core.database import get_db
from ..core.security import get_current_user, require_roles, hash_password
from ..core.audit import log_audit
from ..schemas.admission_schema import AdmissionApplicationCreate
from ..schemas.auth_schema import User
from ..schemas.student_schema import Student
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api/admissions", tags=["Admissions"])


from ..schemas.admission_schema import AdmissionApplicationCreate
from ..services.admission_service import AdmissionService, get_admission_service

@router.post("", response_model=dict)
async def create_admission_application(
    app_data: AdmissionApplicationCreate,
    user: dict = Depends(require_roles(["admin"])),
    admission_service: AdmissionService = Depends(get_admission_service)
):
    doc = await admission_service.create_application(app_data, user["id"])
    return {"message": "Admission application submitted", "application": doc}

@router.get("", response_model=List[dict])
async def get_admission_applications(
    status: Optional[str] = None,
    department_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    user: dict = Depends(get_current_user),
    admission_service: AdmissionService = Depends(get_admission_service)
):
    return await admission_service.get_applications(user, status, department_id, skip=skip, limit=limit)

@router.put("/{app_id}/verify", response_model=dict)
async def verify_admission(
    app_id: str, 
    user: dict = Depends(require_roles(["admin"])),
    admission_service: AdmissionService = Depends(get_admission_service)
):
    await admission_service.verify_application(app_id, user["id"])
    return {"message": "Application verified by office"}

@router.put("/{app_id}/hod-approve", response_model=dict)
async def hod_approve_admission(
    app_id: str,
    approved: bool = True,
    rejection_reason: str = "",
    user: dict = Depends(require_roles(["hod"])),
    admission_service: AdmissionService = Depends(get_admission_service)
):
    await admission_service.hod_review(app_id, approved, rejection_reason, user["id"])
    return {"message": "Application reviewed by HOD"}

@router.put("/{app_id}/principal-approve", response_model=dict)
async def principal_approve_admission(
    app_id: str,
    approved: bool = True,
    rejection_reason: str = "",
    user: dict = Depends(require_roles(["principal"])),
    admission_service: AdmissionService = Depends(get_admission_service)
):
    return await admission_service.principal_approve(app_id, approved, rejection_reason, user["id"])
