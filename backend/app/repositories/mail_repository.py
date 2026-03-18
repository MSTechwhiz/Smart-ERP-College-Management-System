from __future__ import annotations

from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..core.database import get_db
from ..utils.mongo_utils import clean_mongo_doc
from fastapi import Depends

class MailRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create(self, doc: Dict[str, Any]) -> str:
        await self.db.mails.insert_one(doc)
        doc.pop("_id", None)
        return doc["id"]

    async def get_by_id(self, mail_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.mails.find_one({"id": mail_id, "to_user_id": user_id}, {"_id": 0})

    async def update(self, mail_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.db.mails.update_one({"id": mail_id}, {"$set": update_data})
        return result.modified_count > 0

    async def list_mails(self, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        docs = await self.db.mails.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
        return [clean_mongo_doc(d) for d in docs]

def get_mail_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> MailRepository:
    return MailRepository(db)
