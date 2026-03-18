from __future__ import annotations

from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..core.database import get_db
from fastapi import Depends

class TimetableRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create_class_entry(self, doc: Dict[str, Any]) -> str:
        await self.db.today_classes.insert_one(doc)
        doc.pop("_id", None)
        return doc["id"]

    async def get_class_entries(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.db.today_classes.find(query, {"_id": 0}).sort("period", 1).skip(skip).limit(limit).to_list(None)

    async def update_class_entry(self, entry_id: str, faculty_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.db.today_classes.update_one(
            {"id": entry_id, "faculty_id": faculty_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_class_entry(self, entry_id: str, faculty_id: str) -> bool:
        result = await self.db.today_classes.delete_one({"id": entry_id, "faculty_id": faculty_id})
        return result.deleted_count > 0

    async def get_timetable_entries(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.db.timetable.find(query, {"_id": 0}).sort("period", 1).skip(skip).limit(limit).to_list(None)

def get_timetable_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> TimetableRepository:
    return TimetableRepository(db)
