from __future__ import annotations

from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..core.database import get_db
from ..utils.mongo_utils import clean_mongo_doc
from fastapi import Depends


class AnnouncementRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create(self, doc: Dict[str, Any]) -> str:
        await self.db.announcements.insert_one(doc)
        doc.pop("_id", None)
        return doc["id"]

    async def get_by_id(self, ann_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.db.announcements.find_one({"id": ann_id}, {"_id": 0})
        return clean_mongo_doc(doc) if doc else None

    async def update(self, ann_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.db.announcements.update_one({"id": ann_id}, {"$set": update_data})
        return result.modified_count > 0

    async def list_announcements(self, query: Dict[str, Any], skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        docs = await self.db.announcements.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        return [clean_mongo_doc(d) for d in docs]

    async def create_notifications(self, notifications: List[Dict[str, Any]]) -> int:
        if not notifications:
            return 0
        result = await self.db.notifications.insert_many(notifications)
        for n in notifications: n.pop("_id", None)
        return len(result.inserted_ids)

def get_announcement_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> AnnouncementRepository:
    return AnnouncementRepository(db)
