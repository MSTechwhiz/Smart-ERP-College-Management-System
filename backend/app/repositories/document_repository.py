from typing import List, Optional, Dict, Any
from ..core.database import get_db
from datetime import datetime, timezone

class DocumentRepository:
    def __init__(self):
        self.db = get_db()

    async def create_request(self, doc_data: Dict[str, Any]) -> Dict[str, Any]:
        await self.db.document_requests.insert_one(doc_data)
        doc_data.pop("_id", None)
        return doc_data

    async def get_request_by_id(self, request_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.document_requests.find_one({"id": request_id}, {"_id": 0})

    async def get_requests_with_enrichment(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        pipeline = [
            {"$match": query},
            {"$sort": {"created_at": -1}},
            {
                "$lookup": {
                    "from": "students",
                    "localField": "student_id",
                    "foreignField": "id",
                    "as": "student_info"
                }
            },
            {"$unwind": {"path": "$student_info", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "student_info.user_id",
                    "foreignField": "id",
                    "as": "user_info"
                }
            },
            {"$unwind": {"path": "$user_info", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "departments",
                    "localField": "student_info.department_id",
                    "foreignField": "id",
                    "as": "dept_info"
                }
            },
            {"$unwind": {"path": "$dept_info", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "student_id": 1,
                    "document_type": 1,
                    "status": 1,
                    "current_level": 1,
                    "remarks": 1,
                    "created_at": 1,
                    "updated_at": 1,
                    "workflow_history": 1,
                    "delivery_type": 1,
                    "file_url": 1,
                    "roll_number": "$student_info.roll_number",
                    "batch": "$student_info.batch",
                    "student_name": "$user_info.name",
                    "student_email": "$user_info.email",
                    "department": {
                        "name": "$dept_info.name",
                        "code": "$dept_info.code"
                    }
                }
            },
            {"$skip": skip},
            {"$limit": limit}
        ]
        return await self.db.document_requests.aggregate(pipeline).to_list(None)

    async def update_request(self, request_id: str, update_data: Dict[str, Any], workflow_entry: Optional[Dict[str, Any]] = None) -> bool:
        update_query = {"$set": update_data}
        if workflow_entry:
            update_query["$push"] = {"workflow_history": workflow_entry}
        
        result = await self.db.document_requests.update_one(
            {"id": request_id},
            update_query
        )
        return result.modified_count > 0

    async def get_student_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.students.find_one({"user_id": user_id}, {"_id": 0})

    async def get_student_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.students.find_one({"id": student_id}, {"_id": 0})
