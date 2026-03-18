from __future__ import annotations

from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..core.database import get_db
from fastapi import Depends

class AdmissionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create(self, doc: Dict[str, Any]) -> str:
        await self.db.admissions.insert_one(doc)
        doc.pop("_id", None)
        return doc["id"]

    async def get_by_id(self, app_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.admissions.find_one({"id": app_id}, {"_id": 0})

    async def update(self, app_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.db.admissions.update_one({"id": app_id}, {"$set": update_data})
        return result.modified_count > 0

    async def list_applications(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.db.admissions.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(None)

    async def count_students_in_batch(self, department_id: str, batch_year: str) -> int:
        return await self.db.students.count_documents({
            "department_id": department_id, 
            "batch": {"$regex": f"^{batch_year}"}
        })

def get_admission_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> AdmissionRepository:
    return AdmissionRepository(db)
