from __future__ import annotations

from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..core.database import get_db
from fastapi import Depends

class SubjectRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create(self, doc: Dict[str, Any]) -> str:
        await self.db.subjects.insert_one(doc)
        doc.pop("_id", None)
        return doc["id"]

    async def get_by_id(self, subject_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.subjects.find_one({"id": subject_id}, {"_id": 0})

    async def update(self, subject_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.db.subjects.update_one({"id": subject_id}, {"$set": update_data})
        return result.modified_count > 0

    async def delete(self, subject_id: str) -> bool:
        result = await self.db.subjects.delete_one({"id": subject_id})
        return result.deleted_count > 0

    async def list_subjects(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.db.subjects.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(None)

    async def create_mapping(self, doc: Dict[str, Any]) -> str:
        await self.db.subject_faculty_mappings.insert_one(doc)
        doc.pop("_id", None)
        return doc["id"]

    async def list_mappings(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.db.subject_faculty_mappings.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(None)

def get_subject_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> SubjectRepository:
    return SubjectRepository(db)
