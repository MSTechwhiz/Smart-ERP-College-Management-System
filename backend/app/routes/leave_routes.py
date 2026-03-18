from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from ..core.database import get_db
from ..core.security import get_current_user, require_roles
from ..schemas.leave_schema import LeaveRequest, LeaveRequestCreate
from ..services.leave_service import LeaveService, get_leave_service
from datetime import datetime, timezone

router = APIRouter(prefix="/api/leave-requests", tags=["leave"])

@router.post("/apply", response_model=dict)
async def submit_leave_request(
    leave_data: LeaveRequestCreate,
    user: dict = Depends(require_roles(["student"])),
    leave_service: LeaveService = Depends(get_leave_service)
):
    doc = await leave_service.submit_leave_request(leave_data, user["id"])
    return {"message": "Leave request submitted", "leave_request": doc}

@router.get("", response_model=List[dict])
async def get_leave_requests(
    status: Optional[str] = None,
    user: dict = Depends(get_current_user),
    leave_service: LeaveService = Depends(get_leave_service)
):
    return await leave_service.get_leave_requests(user, status)

@router.get("/hod/pending", response_model=List[dict])
async def get_hod_pending_leave_requests(
    user: dict = Depends(require_roles(["hod"])),
    leave_service: LeaveService = Depends(get_leave_service)
):
    """Get pending leave requests for the HOD's department"""
    # Note: get_leave_requests service already filters by dept if user is HOD
    return await leave_service.get_leave_requests(user, "Pending")

@router.put("/{request_id}/approve", response_model=dict)
async def approve_leave_request(
    request_id: str,
    approved: bool,
    user: dict = Depends(require_roles(["hod"])),
    leave_service: LeaveService = Depends(get_leave_service)
):
    return await leave_service.approve_leave_request(request_id, approved, user["id"])
