from typing import List, Optional, Dict, Any
from ..core.database import get_db
from datetime import datetime, timezone

class AIRepository:
    def __init__(self):
        self.db = get_db()

    async def get_chat_session(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.chat_sessions.find_one({"id": session_id, "user_id": user_id}, {"_id": 0})

    async def create_chat_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        await self.db.chat_sessions.insert_one(session_data)
        session_data.pop("_id", None)
        return session_data

    async def update_chat_session(self, session_id: str, messages: List[Dict[str, Any]]) -> bool:
        result = await self.db.chat_sessions.update_one(
            {"id": session_id},
            {
                "$push": {"messages": {"$each": messages}},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        return result.modified_count > 0

    async def get_user_sessions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        return await self.db.chat_sessions.find(
            {"user_id": user_id}, 
            {"_id": 0, "id": 1, "created_at": 1, "updated_at": 1}
        ).sort("updated_at", -1).limit(limit).to_list(None)

    async def delete_session(self, session_id: str, user_id: str) -> bool:
        result = await self.db.chat_sessions.delete_one({"id": session_id, "user_id": user_id})
        return result.deleted_count > 0

    async def get_student_knowledge_data(self, user_id: str) -> Dict[str, Any]:
        # Using aggregation to get all student related data in one go
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$lookup": {
                    "from": "attendance",
                    "localField": "id",
                    "foreignField": "student_id",
                    "as": "attendance"
                }
            },
            {
                "$lookup": {
                    "from": "fee_payments",
                    "localField": "id",
                    "foreignField": "student_id",
                    "as": "fees"
                }
            },
            {
                "$lookup": {
                    "from": "departments",
                    "localField": "department_id",
                    "foreignField": "id",
                    "as": "dept"
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "cgpa": 1,
                    "department_id": 1,
                    "dept_name": {"$arrayElemAt": ["$dept.name", 0]},
                    "attendance_total": {"$size": "$attendance"},
                    "attendance_present": {
                        "$size": {
                            "$filter": {
                                "input": "$attendance",
                                "as": "att",
                                "cond": {"$eq": ["$$att.status", "present"]}
                            }
                        }
                    },
                    "pending_fees": {
                        "$sum": {
                            "$map": {
                                "input": {
                                    "$filter": {
                                        "input": "$fees",
                                        "as": "fee",
                                        "cond": {"$ne": ["$$fee.status", "completed"]}
                                    }
                                },
                                "as": "f",
                                "in": "$$f.amount"
                            }
                        }
                    }
                }
            }
        ]
        results = await self.db.students.aggregate(pipeline).to_list(1)
        return results[0] if results else {}

    async def get_faculty_knowledge_data(self, department_id: str) -> Dict[str, Any]:
        dept = await self.db.departments.find_one({"id": department_id}, {"_id": 0, "name": 1})
        student_count = await self.db.students.count_documents({"department_id": department_id})
        return {
            "dept_name": dept["name"] if dept else "Unknown",
            "student_count": student_count
        }

    async def get_recent_announcements(self, role: str, limit: int = 3) -> List[str]:
        query = {
            "is_active": True, 
            "is_deleted": {"$ne": True}, 
            "publish_date": {"$lte": datetime.now(timezone.utc).isoformat()}
        }
        query["$or"] = [{"target_roles": []}, {"target_roles": role}]
        ann_list = await self.db.announcements.find(query, {"_id": 0, "title": 1}).sort("publish_date", -1).limit(limit).to_list(None)
        return [a["title"] for a in ann_list]

    async def get_student_risk_data(self, student_id: str) -> Optional[Dict[str, Any]]:
        pipeline = [
            {"$match": {"id": student_id}},
            {
                "$lookup": {
                    "from": "attendance",
                    "localField": "id",
                    "foreignField": "student_id",
                    "as": "attendance"
                }
            },
            {
                "$lookup": {
                    "from": "marks",
                    "localField": "id",
                    "foreignField": "student_id",
                    "as": "marks"
                }
            },
            {
                "$lookup": {
                    "from": "fee_payments",
                    "localField": "id",
                    "foreignField": "student_id",
                    "as": "fees"
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "roll_number": 1,
                    "user_id": 1,
                    "attendance": 1,
                    "marks": 1,
                    "pending_fees": {
                        "$filter": {
                            "input": "$fees",
                            "as": "fee",
                            "cond": {"$eq": ["$$fee.status", "pending"]}
                        }
                    }
                }
            }
        ]
        results = await self.db.students.aggregate(pipeline).to_list(1)
        return results[0] if results else None

    async def get_department_risk_data(self, department_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        pipeline = [
            {"$match": {"department_id": department_id}},
            {
                "$lookup": {
                    "from": "attendance",
                    "localField": "id",
                    "foreignField": "student_id",
                    "as": "attendance"
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "id",
                    "as": "user"
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "roll_number": 1,
                    "name": {"$arrayElemAt": ["$user.name", 0]},
                    "attendance_total": {"$size": "$attendance"},
                    "attendance_present": {
                        "$size": {
                            "$filter": {
                                "input": "$attendance",
                                "as": "att",
                                "cond": {"$in": ["$$att.status", ["present", "od"]]}
                            }
                        }
                    }
                }
            },
            {"$skip": skip},
            {"$limit": limit}
        ]
        return await self.db.students.aggregate(pipeline).to_list(None)
