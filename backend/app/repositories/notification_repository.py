from __future__ import annotations

from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..core.database import get_db
from ..utils.mongo_utils import clean_mongo_doc
from fastapi import Depends

class NotificationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create(self, doc: Dict[str, Any]) -> str:
        await self.db.notifications.insert_one(doc)
        doc.pop("_id", None)
        return doc["id"]

    async def create_many(self, docs: List[Dict[str, Any]]) -> int:
        if not docs: return 0
        result = await self.db.notifications.insert_many(docs)
        for d in docs: d.pop("_id", None)
        return len(result.inserted_ids)

    async def get_by_id(self, notification_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.notifications.find_one({"id": notification_id, "user_id": user_id}, {"_id": 0})

    async def update(self, query: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        result = await self.db.notifications.update_many(query, {"$set": update_data})
        return result.modified_count

    async def delete(self, notification_id: str, user_id: str) -> bool:
        result = await self.db.notifications.delete_one({"id": notification_id, "user_id": user_id})
        return result.deleted_count > 0

    async def list_notifications(self, query: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
        docs = await self.db.notifications.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(None)
        return [clean_mongo_doc(d) for d in docs]

def get_notification_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> NotificationRepository:
    return NotificationRepository(db)
