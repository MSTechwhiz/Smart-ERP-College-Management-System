from __future__ import annotations

from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import UpdateOne
from ..core.database import get_db
from fastapi import Depends

class AttendanceRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.attendance

    async def upsert_attendance(self, student_id: str, subject_id: str, date: str, attendance_doc: Dict[str, Any]) -> bool:
        result = await self.collection.update_one(
            {"student_id": student_id, "subject_id": subject_id, "date": date},
            {"$set": attendance_doc},
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None

    async def bulk_upsert_attendance(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        
        operations = [
            UpdateOne(
                {"student_id": r["student_id"], "subject_id": r["subject_id"], "date": r["date"]},
                {"$set": r},
                upsert=True
            ) for r in records
        ]
        result = await self.collection.bulk_write(operations)
        return result.upserted_count + result.modified_count

    async def get_attendance(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.collection.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(None)

    async def get_summary(self, student_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        pipeline = [
            {"$match": {"student_id": student_id}},
            {"$group": {
                "_id": "$subject_id",
                "total": {"$sum": 1},
                "present": {"$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}},
                "absent": {"$sum": {"$cond": [{"$eq": ["$status", "absent"]}, 1, 0]}},
                "od": {"$sum": {"$cond": [{"$eq": ["$status", "od"]}, 1, 0]}}
            }},
            {"$lookup": {
                "from": "subjects",
                "localField": "_id",
                "foreignField": "id",
                "as": "subject_info"
            }},
            {"$unwind": {"path": "$subject_info", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "_id": 0,
                "subject_id": "$_id",
                "subject_name": {"$ifNull": ["$subject_info.name", "Unknown"]},
                "subject_code": {"$ifNull": ["$subject_info.code", "UNK"]},
                "total": 1,
                "present": 1,
                "absent": 1,
                "od": 1,
                "percentage": {
                    "$cond": [
                        {"$gt": ["$total", 0]},
                        {"$round": [{"$multiply": [{"$divide": [{"$add": ["$present", "$od"]}, "$total"]}, 100]}, 2]},
                        0
                    ]
                }
            }},
            {"$skip": skip},
            {"$limit": limit}
        ]
        return await self.collection.aggregate(pipeline).to_list(None)

def get_attendance_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> AttendanceRepository:
    return AttendanceRepository(db)
