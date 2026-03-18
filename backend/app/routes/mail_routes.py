from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from ..core.database import get_db
from ..core.security import get_current_user, require_roles
from ..schemas.mail_schema import Mail, MailCreate
from ..services.mail_service import MailService, get_mail_service
from ..websocket.manager import manager
from datetime import datetime, timezone

router = APIRouter(prefix="/api", tags=["Mail"])

@router.post("/mail", response_model=dict)
async def send_mail(
    mail_data: MailCreate, 
    user: dict = Depends(get_current_user),
    mail_service: MailService = Depends(get_mail_service)
):
    doc = await mail_service.send_mail(mail_data, user)
    return {"message": "Mail sent" if not mail_data.is_draft else "Draft saved", "mail": doc}

@router.get("/mail/inbox", response_model=List[dict])
async def get_inbox(
    user: dict = Depends(get_current_user),
    mail_service: MailService = Depends(get_mail_service)
):
    return await mail_service.get_inbox(user["id"])

@router.get("/mail/sent", response_model=List[dict])
async def get_sent_mails(
    user: dict = Depends(get_current_user),
    mail_service: MailService = Depends(get_mail_service)
):
    return await mail_service.get_sent_mails(user["id"])

@router.get("/mail/drafts", response_model=List[dict])
async def get_drafts(
    user: dict = Depends(get_current_user),
    mail_service: MailService = Depends(get_mail_service)
):
    query = {"from_user_id": user["id"], "is_draft": True}
    return await mail_service.mail_repo.list_mails(query)

@router.put("/mail/{mail_id}/read", response_model=dict)
async def mark_mail_read(
    mail_id: str, 
    user: dict = Depends(get_current_user),
    mail_service: MailService = Depends(get_mail_service)
):
    await mail_service.mark_read(mail_id, user["id"])
    return {"message": "Mail marked as read"}

@router.put("/mail/{mail_id}/archive", response_model=dict)
async def archive_mail(
    mail_id: str, 
    user: dict = Depends(get_current_user),
    mail_service: MailService = Depends(get_mail_service)
):
    await mail_service.archive_mail(mail_id, user["id"])
    return {"message": "Mail archived"}

@router.get("/mail/users", response_model=List[dict])
async def get_mail_recipients(
    user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    db = get_db()
    """Get list of users the current user can send mail to based on role"""
    query = {}
    
    if user["role"] == "student":
        # Students can mail faculty and HOD
        query["role"] = {"$in": ["faculty", "hod"]}
        query["department_id"] = user.get("department_id")
    elif user["role"] == "faculty":
        # Faculty can mail students, other faculty, and HOD
        query["$or"] = [
            {"role": "student", "department_id": user.get("department_id")},
            {"role": {"$in": ["faculty", "hod"]}, "department_id": user.get("department_id")}
        ]
    elif user["role"] == "hod":
        # HOD can mail faculty, principal
        query["role"] = {"$in": ["faculty", "principal"]}
    elif user["role"] in ["principal", "admin"]:
        # Principal and admin can mail anyone
        pass
    
    users = await db.users.find(query, {"_id": 0, "id": 1, "name": 1, "email": 1, "role": 1}).skip(skip).limit(limit).to_list(None)
    return users
