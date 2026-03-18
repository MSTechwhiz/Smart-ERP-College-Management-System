from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from ..core.database import get_db
from ..core.security import get_current_user, require_roles
from ..core.audit import log_audit
from ..schemas.announcement_schema import Announcement, AnnouncementCreate, AnnouncementUpdate
from ..services.announcement_service import AnnouncementService, get_announcement_service
from ..websocket.manager import manager
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api/announcements", tags=["Announcements"])

@router.post("", response_model=dict)
async def create_announcement(
    announcement_data: AnnouncementCreate,
    user: dict = Depends(require_roles(["principal", "admin", "hod", "faculty"])),
    ann_service: AnnouncementService = Depends(get_announcement_service)
):
    doc = await ann_service.create_announcement(announcement_data, user)
    return {"message": "Announcement created", "announcement": doc}

@router.get("", response_model=List[dict])
async def get_announcements(
    skip: int = 0,
    limit: int = 50,
    user: dict = Depends(get_current_user),
    ann_service: AnnouncementService = Depends(get_announcement_service)
):
    return await ann_service.get_announcements(user, skip=skip, limit=limit)


@router.put("/{ann_id}", response_model=dict)
async def update_announcement(
    ann_id: str,
    ann_data: AnnouncementUpdate,
    user: dict = Depends(require_roles(["principal", "admin"]))
):
    db = get_db()
    from ..core.audit import log_audit
    """Update announcement"""
    ann = await db.announcements.find_one({"id": ann_id}, {"_id": 0})
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    update_data = {k: v for k, v in ann_data.model_dump().items() if v is not None}

    allowed_targets = {
        "admin": ["principal", "hod", "faculty", "student"],
        "principal": ["hod", "faculty", "student"],
    }
    if "target_roles" in update_data:
        requested_targets = update_data.get("target_roles") or []
        invalid = [r for r in requested_targets if r not in allowed_targets.get(user["role"], [])]
        if invalid:
            raise HTTPException(status_code=403, detail="Invalid announcement target")
    
    if "publish_date" in update_data and isinstance(update_data["publish_date"], datetime):
        update_data["publish_date"] = update_data["publish_date"].isoformat()
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.announcements.update_one({"id": ann_id}, {"$set": update_data})
    
    updated = await db.announcements.find_one({"id": ann_id}, {"_id": 0})
    # Log audit
    await log_audit(user["id"], "update", "announcement", ann_id, ann, updated, user_name=user["name"], user_role=user["role"])
    
    return {"message": "Announcement updated", "announcement": updated}


@router.delete("/{ann_id}", response_model=dict)
async def delete_announcement(ann_id: str, user: dict = Depends(require_roles(["principal", "admin"]))):
    db = get_db()
    from ..core.audit import log_audit
    """Delete announcement (Soft Delete)"""
    ann = await db.announcements.find_one({"id": ann_id}, {"_id": 0})
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    await db.announcements.update_one({"id": ann_id}, {"$set": {"is_deleted": True, "is_active": False, "deleted_at": datetime.now(timezone.utc).isoformat()}})
    # Log audit
    await log_audit(user["id"], "delete", "announcement", ann_id, ann, None, user_name=user["name"], user_role=user["role"])
    
    return {"message": "Announcement deleted"}


@router.get("/admin/list", response_model=List[dict])
async def get_admin_announcements(
    user: dict = Depends(require_roles(["principal", "admin"])),
    skip: int = 0,
    limit: int = 100
):
    db = get_db()
    """Get all announcements for admin view (including inactive)"""
    query = {"is_deleted": {"$ne": True}}
    announcements = await db.announcements.find(query, {"_id": 0}).sort("publish_date", -1).skip(skip).limit(limit).to_list(None)
    
    # Enrich with creator info - Optimized batch fetch
    creator_ids = list({ann["created_by"] for ann in announcements})
    creators = await db.users.find({"id": {"$in": creator_ids}}, {"_id": 0, "id": 1, "name": 1, "role": 1}).to_list(None)
    creator_map = {c["id"]: c for c in creators}
    
    for ann in announcements:
        creator = creator_map.get(ann["created_by"])
        if creator:
            ann["created_by_name"] = creator["name"]
            ann["created_by_role"] = creator["role"]
    
    return announcements
