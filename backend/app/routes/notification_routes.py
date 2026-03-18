from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from ..core.database import get_db
from ..core.security import get_current_user, require_roles
from ..websocket.manager import manager
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


from ..services.notification_service import NotificationService, get_notification_service

@router.post("/automated-check")
async def run_automated_notifications(
    background_tasks: BackgroundTasks,
    user: dict = Depends(require_roles(["principal", "admin"])),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Run automated checks for deadlines, fees, and attendance shortages"""
    background_tasks.add_task(notification_service.run_automated_checks)
    return {"message": "Automated checks started in background"}

@router.post("", response_model=dict)
async def create_notification(
    user_id: str,
    title: str,
    message: str,
    notification_type: str = "general",
    priority: str = "normal",
    action_url: Optional[str] = None,
    metadata: Optional[dict] = None,
    current_user: dict = Depends(require_roles(["principal", "admin", "hod"])),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Create notification for a user"""
    data = {
        "user_id": user_id,
        "title": title,
        "message": message,
        "notification_type": notification_type,
        "priority": priority,
        "action_url": action_url,
        "metadata": metadata
    }
    notification = await notification_service.create_notification(data)
    return {"message": "Notification created", "notification": notification}

@router.get("/my", response_model=List[dict])
async def get_my_notifications(
    unread_only: bool = False,
    limit: int = 50,
    user: dict = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    return await notification_service.get_my_notifications(user["id"], unread_only, limit)

@router.put("/{notification_id}/read", response_model=dict)
async def mark_notification_read(
    notification_id: str, 
    user: dict = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    await notification_service.mark_read(notification_id, user["id"])
    return {"message": "Notification marked as read"}

@router.put("/mark-all-read", response_model=dict)
async def mark_all_notifications_read(
    user: dict = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    await notification_service.mark_all_read(user["id"])
    return {"status": "success", "message": "All notifications marked as read"}

@router.delete("/{notification_id}", response_model=dict)
async def delete_notification(
    notification_id: str, 
    user: dict = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    await notification_service.delete_notification(notification_id, user["id"])
    return {"status": "success", "message": "Notification deleted"}
