from __future__ import annotations

from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..core.database import get_db
from fastapi import Depends

class LeaveRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create(self, doc: Dict[str, Any]) -> str:
        await self.db.leave_requests.insert_one(doc)
        doc.pop("_id", None)
        return doc["id"]

    async def get_by_id(self, request_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.leave_requests.find_one({"id": request_id}, {"_id": 0})

    async def update(self, request_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.db.leave_requests.update_one({"id": request_id}, {"$set": update_data})
        return result.modified_count > 0

    async def list_requests(self, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        return await self.db.leave_requests.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)

def get_leave_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> LeaveRepository:
    return LeaveRepository(db)
