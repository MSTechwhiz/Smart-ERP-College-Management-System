from __future__ import annotations

from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.database import get_db
from ..utils.mongo_utils import clean_mongo_doc


class DepartmentRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.departments

    async def get_by_id(self, department_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"id": department_id}, {"_id": 0})
        return clean_mongo_doc(doc) if doc else None

    async def get_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"code": code}, {"_id": 0})
        return clean_mongo_doc(doc) if doc else None

    async def create(self, department_dict: Dict[str, Any]) -> str:
        await self.collection.insert_one(department_dict)
        department_dict.pop("_id", None)
        return department_dict["id"]

    async def update(self, department_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.collection.update_one({"id": department_id}, {"$set": update_data})
        return result.modified_count > 0

    async def delete(self, department_id: str) -> bool:
        result = await self.collection.delete_one({"id": department_id})
        return result.deleted_count > 0

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        docs = await self.collection.find({}, {"_id": 0}).skip(skip).limit(limit).to_list(None)
        return [clean_mongo_doc(d) for d in docs]


from fastapi import Depends

def get_department_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> DepartmentRepository:
    return DepartmentRepository(db)
