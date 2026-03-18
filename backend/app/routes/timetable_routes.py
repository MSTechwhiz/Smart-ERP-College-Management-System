from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from ..core.database import get_db
from ..core.security import get_current_user, require_roles
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api/timetable", tags=["Today Class / Timetable"])


from ..services.timetable_service import TimetableService, get_timetable_service

@router.post("/manual", response_model=dict)
async def create_manual_class_entry(
    date: str,
    period: int,
    subject_id: Optional[str] = None,
    topic: Optional[str] = None,
    notes: Optional[str] = None,
    user: dict = Depends(require_roles(["faculty"])),
    timetable_service: TimetableService = Depends(get_timetable_service)
):
    data = {"date": date, "period": period, "subject_id": subject_id, "topic": topic, "notes": notes}
    entry = await timetable_service.create_manual_entry(data, user["id"])
    return {"message": "Class entry created", "entry": entry}

@router.get("/today", response_model=List[dict])
async def get_today_classes(
    date: Optional[str] = None,
    user: dict = Depends(require_roles(["faculty"])),
    timetable_service: TimetableService = Depends(get_timetable_service)
):
    return await timetable_service.get_today_classes(date, user["id"])

@router.put("/manual/{entry_id}", response_model=dict)
async def update_manual_class_entry(
    entry_id: str,
    topic: Optional[str] = None,
    notes: Optional[str] = None,
    is_completed: Optional[bool] = None,
    user: dict = Depends(require_roles(["faculty"])),
    timetable_service: TimetableService = Depends(get_timetable_service)
):
    update_data = {}
    if topic is not None: update_data["topic"] = topic
    if notes is not None: update_data["notes"] = notes
    if is_completed is not None: update_data["is_completed"] = is_completed
    
    updated = await timetable_service.update_entry(entry_id, update_data, user["id"])
    return {"message": "Entry updated", "entry": updated}

@router.delete("/manual/{entry_id}", response_model=dict)
async def delete_manual_class_entry(
    entry_id: str, 
    user: dict = Depends(require_roles(["faculty"])),
    timetable_service: TimetableService = Depends(get_timetable_service)
):
    await timetable_service.delete_entry(entry_id, user["id"])
    return {"message": "Entry deleted"}

