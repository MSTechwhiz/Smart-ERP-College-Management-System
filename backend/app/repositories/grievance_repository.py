from __future__ import annotations

from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..core.database import get_db
from fastapi import Depends

class GrievanceRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create(self, doc: Dict[str, Any]) -> str:
        await self.db.grievances.insert_one(doc)
        doc.pop("_id", None)
        return doc["id"]

    async def get_by_id(self, grievance_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.grievances.find_one({"id": grievance_id}, {"_id": 0})

    async def update(self, grievance_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.db.grievances.update_one({"id": grievance_id}, {"$set": update_data})
        return result.modified_count > 0

    async def update_workflow(self, grievance_id: str, update_data: Dict[str, Any], workflow_entry: Dict[str, Any]) -> bool:
        result = await self.db.grievances.update_one(
            {"id": grievance_id},
            {
                "$set": update_data,
                "$push": {"workflow_history": workflow_entry}
            }
        )
        return result.modified_count > 0

    async def delete(self, grievance_id: str) -> bool:
        result = await self.db.grievances.delete_one({"id": grievance_id})
        return result.deleted_count > 0

    async def list_grievances(self, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        return await self.db.grievances.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)

    async def add_comment(self, comment_doc: Dict[str, Any]) -> str:
        await self.db.grievance_comments.insert_one(comment_doc)
        comment_doc.pop("_id", None)
        return comment_doc["id"]

    async def get_comments(self, grievance_id: str) -> List[Dict[str, Any]]:
        return await self.db.grievance_comments.find({"grievance_id": grievance_id}, {"_id": 0}).sort("created_at", 1).to_list(None)

def get_grievance_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> GrievanceRepository:
    return GrievanceRepository(db)
