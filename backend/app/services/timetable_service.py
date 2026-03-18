from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid
from fastapi import Depends, HTTPException
from ..repositories.timetable_repository import TimetableRepository, get_timetable_repository
from ..repositories.faculty_repository import FacultyRepository, get_faculty_repository
from ..repositories.subject_repository import SubjectRepository, get_subject_repository

class TimetableService:
    def __init__(
        self, 
        timetable_repo: TimetableRepository, 
        faculty_repo: FacultyRepository,
        subject_repo: SubjectRepository
    ):
        self.timetable_repo = timetable_repo
        self.faculty_repo = faculty_repo
        self.subject_repo = subject_repo

    async def create_manual_entry(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        faculty = await self.faculty_repo.get_by_user_id(user_id)
        if not faculty: raise HTTPException(status_code=404, detail="Faculty profile not found")
        
        entry = {
            "id": str(uuid.uuid4()),
            "faculty_id": faculty["id"],
            "is_completed": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            **data
        }
        await self.timetable_repo.create_class_entry(entry)
        return entry

    async def get_today_classes(self, date: Optional[str], user_id: str) -> List[Dict[str, Any]]:
        faculty = await self.faculty_repo.get_by_user_id(user_id)
        if not faculty: raise HTTPException(status_code=404, detail="Faculty profile not found")
        
        if not date: date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        manual_entries = await self.timetable_repo.get_class_entries({"faculty_id": faculty["id"], "date": date})
        
        day_of_week = datetime.strptime(date, "%Y-%m-%d").weekday()
        timetable_entries = await self.timetable_repo.get_timetable_entries({
            "faculty_id": faculty["id"], 
            "day_of_week": day_of_week, 
            "is_active": True
        })
        
        all_entries = []
        # Optimization: Batch fetch subjects
        subject_ids = set()
        for e in manual_entries: 
            if e.get("subject_id"): subject_ids.add(e["subject_id"])
        for e in timetable_entries: 
            if e.get("subject_id"): subject_ids.add(e["subject_id"])
            
        subjects = await self.subject_repo.list_subjects({"id": {"$in": list(subject_ids)}})
        subject_map = {s["id"]: s for s in subjects}
        
        for entry in manual_entries:
            entry["subject"] = subject_map.get(entry.get("subject_id"))
            entry["source"] = "manual"
            all_entries.append(entry)
            
        for entry in timetable_entries:
            entry["subject"] = subject_map.get(entry.get("subject_id"))
            entry["source"] = "timetable"
            entry["date"] = date
            all_entries.append(entry)
            
        return all_entries

    async def update_entry(self, entry_id: str, update_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        faculty = await self.faculty_repo.get_by_user_id(user_id)
        await self.timetable_repo.update_class_entry(entry_id, faculty["id"], update_data)
        # Fetch updated
        entries = await self.timetable_repo.get_class_entries({"id": entry_id})
        return entries[0] if entries else {}

    async def delete_entry(self, entry_id: str, user_id: str) -> bool:
        faculty = await self.faculty_repo.get_by_user_id(user_id)
        return await self.timetable_repo.delete_class_entry(entry_id, faculty["id"])

def get_timetable_service(
    timetable_repo: TimetableRepository = Depends(get_timetable_repository),
    faculty_repo: FacultyRepository = Depends(get_faculty_repository),
    subject_repo: SubjectRepository = Depends(get_subject_repository)
) -> TimetableService:
    return TimetableService(timetable_repo, faculty_repo, subject_repo)
