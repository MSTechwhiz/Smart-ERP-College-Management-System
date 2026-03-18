from __future__ import annotations

from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..core.database import get_db

class CGPARepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.cgpa_calculations

    async def get_student_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.students.find_one({"user_id": user_id}, {"_id": 0})

    async def get_student_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.students.find_one({"id": student_id}, {"_id": 0})

    async def save_calculation(self, calc_record: Dict[str, Any]) -> str:
        await self.collection.insert_one(calc_record)
        calc_record.pop("_id", None)
        return calc_record["id"]

    async def get_history(self, student_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.collection.find({"student_id": student_id}, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
    async def get_all_calculations(self, student_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.collection.find({"student_id": student_id}, {"_id": 0}).skip(skip).limit(limit).to_list(None)

    async def update_student_cgpa(self, student_id: str, cgpa: float) -> bool:
        result = await self.db.students.update_one({"id": student_id}, {"$set": {"cgpa": cgpa}})
        return result.modified_count > 0

def get_cgpa_repository() -> CGPARepository:
    return CGPARepository(get_db())
