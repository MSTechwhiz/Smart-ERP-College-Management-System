from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from ..core.database import get_db
from ..core.security import get_current_user, require_roles
from ..core.audit import log_audit
from ..schemas.grievance_schema import Grievance, GrievanceCreate, GrievanceUpdate, GrievanceWorkflow
from ..services.grievance_service import GrievanceService, get_grievance_service
from ..websocket.manager import manager
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api/grievances", tags=["Grievances"])

@router.post("", response_model=dict)
async def submit_grievance(
    grievance_data: GrievanceCreate,
    user: dict = Depends(require_roles(["student"])),
    grievance_service: GrievanceService = Depends(get_grievance_service)
):
    doc = await grievance_service.submit_grievance(grievance_data, user)
    return {"message": "Grievance submitted", "grievance": doc}

@router.put("/{grievance_id}", response_model=dict)
async def update_grievance(
    grievance_id: str,
    update_data: GrievanceUpdate,
    user: dict = Depends(get_current_user)
):
    db = get_db()
    """Update grievance (Student who created OR Admin)"""
    grievance = await db.grievances.find_one({"id": grievance_id}, {"_id": 0})
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    
    # Permission check
    is_admin = user["role"] in ["admin", "principal"]
    is_owner = False
    if user["role"] == "student":
        student = await db.students.find_one({"user_id": user["id"]}, {"_id": 0, "id": 1})
        if student and student["id"] == grievance["student_id"]:
            is_owner = True
            
    if not is_admin and not is_owner:
        raise HTTPException(status_code=403, detail="Not authorized to update this grievance")
        
    if is_owner and not is_admin:
        # Students can only update if it hasn't been resolved or moved up significantly
        if grievance["status"] not in ["open", "pending", "in_progress"]:
             raise HTTPException(status_code=400, detail="Cannot update a resolved/closed grievance")
             
    data = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if data:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.grievances.update_one({"id": grievance_id}, {"$set": data})
        
        # Log action in workflow history if status changed
        if "status" in data:
            workflow_entry = {
                "level": user["role"],
                "user_id": user["id"],
                "user_name": user["name"],
                "action": f"status_changed_to_{data['status']}",
                "remarks": f"Status updated by {user['role']}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await db.grievances.update_one(
                {"id": grievance_id},
                {"$push": {"workflow_history": workflow_entry}}
            )
            
    updated = await db.grievances.find_one({"id": grievance_id}, {"_id": 0})
    await log_audit(user["id"], "update", "grievance", grievance_id, grievance, updated, user_name=user["name"], user_role=user["role"])
    return {"message": "Grievance updated", "grievance": updated}

@router.delete("/{grievance_id}", response_model=dict)
async def delete_grievance(grievance_id: str, user: dict = Depends(require_roles(["admin", "principal"]))):
    db = get_db()
    """Delete grievance (Admin/Principal only)"""
    grievance = await db.grievances.find_one({"id": grievance_id}, {"_id": 0})
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
        
    await db.grievances.delete_one({"id": grievance_id})
    await log_audit(user["id"], "delete", "grievance", grievance_id, grievance, None, user_name=user["name"], user_role=user["role"])
    return {"message": "Grievance deleted"}

@router.get("", response_model=List[dict])
async def get_grievances(
    status: Optional[str] = None,
    category: Optional[str] = None,
    user: dict = Depends(get_current_user),
    grievance_service: GrievanceService = Depends(get_grievance_service)
):
    return await grievance_service.get_grievances(user, status, category)

@router.get("/hod/escalated", response_model=List[dict])
async def get_hod_escalated_grievances(
    user: dict = Depends(require_roles(["hod"])),
    grievance_service: GrievanceService = Depends(get_grievance_service)
):
    """Get grievances escalated to HOD level (legacy status)"""
    return await grievance_service.get_grievances(user, status="escalated")

@router.get("/hod/pending", response_model=List[dict])
async def get_hod_pending_grievances(
    user: dict = Depends(require_roles(["hod"])),
    grievance_service: GrievanceService = Depends(get_grievance_service)
):
    """Get grievances pending HOD review"""
    return await grievance_service.get_grievances(user, status="hod_review")

@router.put("/{grievance_id}/forward", response_model=dict)
async def forward_grievance(
    grievance_id: str,
    to_level: str,
    remarks: Optional[str] = None,
    user: dict = Depends(require_roles(["faculty", "hod", "admin"])),
    grievance_service: GrievanceService = Depends(get_grievance_service)
):
    return await grievance_service.forward_grievance(grievance_id, to_level, remarks, user)

@router.put("/{grievance_id}/resolve", response_model=dict)
async def resolve_grievance(
    grievance_id: str,
    resolution: str,
    user: dict = Depends(require_roles(["principal", "admin", "hod", "faculty"])),
    grievance_service: GrievanceService = Depends(get_grievance_service)
):
    return await grievance_service.resolve_grievance(grievance_id, resolution, user)

@router.get("/{grievance_id}", response_model=dict)
async def get_grievance_detail(
    grievance_id: str,
    user: dict = Depends(get_current_user),
    grievance_service: GrievanceService = Depends(get_grievance_service)
):
    return await grievance_service.get_grievance_detail(grievance_id, user)

@router.get("/all", response_model=List[dict])
async def get_all_grievances(
    status: Optional[str] = None,
    category: Optional[str] = None,
    user: dict = Depends(require_roles(["principal", "admin", "hod"])),
    grievance_service: GrievanceService = Depends(get_grievance_service)
):
    return await grievance_service.get_all_grievances(user, status, category)

@router.put("/{grievance_id}/assign", response_model=dict)
async def assign_grievance(
    grievance_id: str,
    assigned_to: str,
    user: dict = Depends(require_roles(["principal", "admin", "hod"])),
    grievance_service: GrievanceService = Depends(get_grievance_service)
):
    return await grievance_service.assign_grievance(grievance_id, assigned_to)

@router.put("/{grievance_id}/escalate", response_model=dict)
async def escalate_grievance(
    grievance_id: str,
    user: dict = Depends(require_roles(["principal", "admin", "hod"])),
    grievance_service: GrievanceService = Depends(get_grievance_service)
):
    return await grievance_service.escalate_grievance(grievance_id)

@router.post("/{grievance_id}/comment", response_model=dict)
async def add_grievance_comment(
    grievance_id: str,
    comment: str,
    user: dict = Depends(get_current_user),
    grievance_service: GrievanceService = Depends(get_grievance_service)
):
    return await grievance_service.add_comment(grievance_id, comment, user)

@router.get("/{grievance_id}/comments", response_model=List[dict])
async def get_grievance_comments(
    grievance_id: str, 
    user: dict = Depends(get_current_user),
    grievance_service: GrievanceService = Depends(get_grievance_service)
):
    return await grievance_service.grievance_repo.get_comments(grievance_id)

