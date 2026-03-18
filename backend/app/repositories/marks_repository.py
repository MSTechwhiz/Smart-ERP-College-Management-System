from __future__ import annotations

from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import UpdateOne
from ..core.database import get_db
from fastapi import Depends

class MarksRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.marks

    async def get_marks_by_criteria(self, criteria: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one(criteria, {"_id": 0})

    async def create_marks(self, marks_doc: Dict[str, Any]) -> str:
        await self.collection.insert_one(marks_doc)
        marks_doc.pop("_id", None)
        return marks_doc["id"]

    async def update_marks(self, marks_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.collection.update_one({"id": marks_id}, {"$set": update_data})
        return result.modified_count > 0

    async def bulk_upsert_marks(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        
        operations = [
            UpdateOne(
                {
                    "student_id": r["student_id"], 
                    "subject_id": r["subject_id"], 
                    "academic_year": r["academic_year"], 
                    "semester": r["semester"]
                },
                {"$set": r},
                upsert=True
            ) for r in records
        ]
        result = await self.collection.bulk_write(operations)
        return result.upserted_count + result.modified_count

    async def get_marks_with_subjects(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        # Handle department_id if it's in the query
        dept_id = query.pop("department_id", None)
        
        pipeline = []
        
        # Initial match for direct marks fields
        if query:
            pipeline.append({"$match": query})
            
        # Join with students to get department info if needed
        pipeline.extend([
            {"$lookup": {
                "from": "students",
                "localField": "student_id",
                "foreignField": "id",
                "as": "student_info"
            }},
            {"$unwind": "$student_info"}
        ])

        # Apply department filter if present
        if dept_id:
            pipeline.append({"$match": {"student_info.department_id": dept_id}})

        pipeline.extend([
            {"$lookup": {
                "from": "subjects",
                "localField": "subject_id",
                "foreignField": "id",
                "as": "subject_info"
            }},
            {"$unwind": {"path": "$subject_info", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "_id": 0,
                "id": 1,
                "student_id": 1,
                "subject_id": 1,
                "academic_year": 1,
                "semester": 1,
                "cia1": 1, "cia2": 1, "cia3": 1, "cia4": 1,
                "model_exam": 1, "assignment": 1, "lab": 1, "semester_exam": 1,
                "total": 1, "grade": 1, "grade_point": 1, "is_locked": 1,
                "subject_name": {"$ifNull": ["$subject_info.name", "Unknown"]},
                "subject_code": {"$ifNull": ["$subject_info.code", "UNK"]},
                "credits": {"$ifNull": ["$subject_info.credits", 0]},
                "department_id": "$student_info.department_id"
            }},
            {"$skip": skip},
            {"$limit": limit}
        ])
        return await self.collection.aggregate(pipeline).to_list(None)

    async def get_semester_gpa(self, student_id: str) -> List[Dict[str, Any]]:
        pipeline = [
            {"$match": {"student_id": student_id, "is_locked": True}},
            {"$lookup": {
                "from": "subjects",
                "localField": "subject_id",
                "foreignField": "id",
                "as": "subject_info"
            }},
            {"$unwind": "$subject_info"},
            {"$group": {
                "_id": "$semester",
                "total_points": {"$sum": {"$multiply": ["$grade_point", "$subject_info.credits"]}},
                "total_credits": {"$sum": "$subject_info.credits"}
            }},
            {"$project": {
                "semester": "$_id",
                "gpa": {
                    "$cond": [
                        {"$gt": ["$total_credits", 0]},
                        {"$round": [{"$divide": ["$total_points", "$total_credits"]}, 2]},
                        0
                    ]
                },
                "credits": "$total_credits",
                "_id": 0
            }},
            {"$sort": {"semester": 1}}
        ]
        return await self.collection.aggregate(pipeline).to_list(None)

def get_marks_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> MarksRepository:
    return MarksRepository(db)
