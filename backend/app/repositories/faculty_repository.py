from __future__ import annotations

from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.database import get_db
from ..utils.mongo_utils import clean_mongo_doc


class FacultyRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.faculty

    async def get_by_id(self, faculty_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"id": faculty_id}, {"_id": 0})
        return clean_mongo_doc(doc) if doc else None

    async def get_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"user_id": user_id}, {"_id": 0})
        return clean_mongo_doc(doc) if doc else None

    async def get_by_employee_id(self, employee_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"employee_id": employee_id}, {"_id": 0})
        return clean_mongo_doc(doc) if doc else None

    async def create(self, faculty_dict: Dict[str, Any]) -> str:
        await self.collection.insert_one(faculty_dict)
        faculty_dict.pop("_id", None)
        return faculty_dict["id"]

    async def update(self, faculty_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.collection.update_one({"id": faculty_id}, {"$set": update_data})
        return result.modified_count > 0

    async def delete(self, faculty_id: str) -> bool:
        result = await self.collection.delete_one({"id": faculty_id})
        return result.deleted_count > 0

    async def list_by_department(self, department_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        docs = await self.collection.find({"department_id": department_id}, {"_id": 0}).skip(skip).limit(limit).to_list(None)
        return [clean_mongo_doc(d) for d in docs]

    async def get_faculty_with_users(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        pipeline = [
            {"$match": query},
            {"$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "id",
                "as": "user_info"
            }},
            {"$unwind": {"path": "$user_info", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "_id": 0,
                "id": 1,
                "user_id": 1,
                "employee_id": 1,
                "department_id": 1,
                "designation": 1,
                "specialization": 1,
                "joining_date": 1,
                "is_class_incharge": 1,
                "incharge_class": 1,
                "name": {"$ifNull": ["$user_info.name", "Unknown"]},
                "email": {"$ifNull": ["$user_info.email", ""]}
            }},
            {"$skip": skip},
            {"$limit": limit}
        ]
        docs = await self.collection.aggregate(pipeline).to_list(None)
        return [clean_mongo_doc(d) for d in docs]


from fastapi import Depends

def get_faculty_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> FacultyRepository:
    return FacultyRepository(db)
