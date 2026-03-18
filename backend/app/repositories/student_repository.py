from __future__ import annotations

from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.database import get_db
from ..utils.mongo_utils import clean_mongo_doc
from ..utils.encryption import Encryption


class StudentRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.students

    async def get_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"id": student_id}, {"_id": 0})
        if doc:
            doc = self._decrypt_pii(doc)
        return clean_mongo_doc(doc) if doc else None

    async def get_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"user_id": user_id}, {"_id": 0})
        return clean_mongo_doc(doc) if doc else None

    async def get_by_roll_number(self, roll_number: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"roll_number": roll_number}, {"_id": 0})
        return clean_mongo_doc(doc) if doc else None

    async def create(self, student_dict: Dict[str, Any]) -> str:
        student_dict = self._encrypt_pii(student_dict)
        await self.collection.insert_one(student_dict)
        student_dict.pop("_id", None)
        return student_dict["id"]

    async def update(self, student_id: str, update_data: Dict[str, Any]) -> bool:
        update_data = self._encrypt_pii(update_data)
        result = await self.collection.update_one({"id": student_id}, {"$set": update_data})
        return result.modified_count > 0
    
    def _encrypt_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pii_fields = ["mobile", "alternate_mobile", "address", "parent_contact", "parent_mobile"]
        new_data = data.copy()
        for field in pii_fields:
            if field in new_data and new_data[field]:
                new_data[field] = Encryption.encrypt(str(new_data[field]))
        return new_data
        
    def _decrypt_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pii_fields = ["mobile", "alternate_mobile", "address", "parent_contact", "parent_mobile"]
        new_data = data.copy()
        for field in pii_fields:
            if field in new_data and new_data[field]:
                new_data[field] = Encryption.decrypt(str(new_data[field]))
        return new_data

    async def delete(self, student_id: str) -> bool:
        result = await self.collection.delete_one({"id": student_id})
        return result.deleted_count > 0

    async def list_by_department(self, department_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        docs = await self.collection.find({"department_id": department_id}, {"_id": 0}).skip(skip).limit(limit).to_list(None)
        return [clean_mongo_doc(d) for d in docs]

    async def count_students_in_batch(self, department_id: str, batch_year: str) -> int:
        return await self.collection.count_documents({
            "department_id": department_id, 
            "batch": {"$regex": f"^{batch_year}"}
        })

    async def get_students_with_users(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        if category := query.get("admission_quota"):
            norm_map = {
                "Management Quota": "(MQ|Management)",
                "7.5 Quota": "7.5",
                "PMSS": "(PMSS|PMMS)",
                "FG Quota": "(FG|GF|F\\.G)",
                "Government Quota": "(GQ|Government|COUNSELLING)"
            }
            if isinstance(category, str) and category in norm_map:
                query["admission_quota"] = {"$regex": norm_map[category], "$options": "i"}
        
        # Handle search separately as it may involve joined fields
        search_term = query.pop("search", None)
        
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
                "roll_number": 1,
                "register_number": 1,
                "department_id": 1,
                "batch": 1,
                "year": 1,
                "semester": 1,
                "section": 1,
                "cgpa": 1,
                "is_active": 1,
                "admission_quota": 1,
                "admission_type": 1,
                "emis_id": 1,
                "parent_name": 1,
                "parent_phone": 1,
                "gender": 1,
                "name": {"$ifNull": ["$user_info.name", "Unknown"]},
                "email": {"$ifNull": ["$user_info.email", ""]}
            }}
        ]
        
        if search_term:
            pipeline.append({
                "$match": {
                    "$or": [
                        {"name": {"$regex": search_term, "$options": "i"}},
                        {"email": {"$regex": search_term, "$options": "i"}},
                        {"roll_number": {"$regex": search_term, "$options": "i"}},
                        {"register_number": {"$regex": search_term, "$options": "i"}}
                    ]
                }
            })
            
        pipeline.append({"$skip": skip})
        if limit is not None:
            pipeline.append({"$limit": limit})
            
        docs = await self.collection.aggregate(pipeline).to_list(None)
        return [clean_mongo_doc(d) for d in docs]

    async def get_student_with_user(self, student_id: str) -> Optional[Dict[str, Any]]:
        pipeline = [
            {"$match": {"id": student_id}},
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
                "roll_number": 1,
                "department_id": 1,
                "batch": 1,
                "year": 1,
                "semester": 1,
                "section": 1,
                "cgpa": 1,
                "is_active": 1,
                "year": 1,
                "semester": 1,
                "admission_quota": 1,
                "emis_id": 1,
                "parent_name": 1,
                "parent_phone": 1,
                "gender": 1,
                "date_of_birth": 1,
                "blood_group": 1,
                "community": 1,
                "aadhar_number": 1,
                "umis_id": 1,
                "emis_id": 1,
                "mobile_number": 1,
                "permanent_address": 1,
                "parent_details": 1,
                "name": {"$ifNull": ["$user_info.name", "Unknown"]},
                "email": {"$ifNull": ["$user_info.email", ""]}
            }}
        ]
        results = await self.collection.aggregate(pipeline).to_list(1)
        return clean_mongo_doc(results[0]) if results else None

    async def get_department(self, department_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.departments.find_one({"id": department_id}, {"_id": 0})

    async def get_faculty_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.faculty.find_one({"user_id": user_id}, {"_id": 0})

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return await self.db.users.find_one({"email": email}, {"_id": 0})

    async def get_documents(self, student_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.db.student_documents.find({"student_id": student_id}, {"_id": 0}).skip(skip).limit(limit).to_list(None)

    async def create_user(self, user_doc: Dict[str, Any]) -> str:
        await self.db.users.insert_one(user_doc)
        user_doc.pop("_id", None)
        return user_doc["id"]


from fastapi import Depends

def get_student_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> StudentRepository:
    return StudentRepository(db)
