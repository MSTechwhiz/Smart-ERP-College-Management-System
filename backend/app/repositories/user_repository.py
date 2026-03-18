from __future__ import annotations

from typing import Any, Dict, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.database import get_db


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"email": email}, {"_id": 0})

    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"id": user_id}, {"_id": 0})

    async def create(self, user_dict: Dict[str, Any]) -> str:
        await self.collection.insert_one(user_dict)
        user_dict.pop("_id", None)
        return user_dict["id"]

    async def update(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.collection.update_one({"id": user_id}, {"$set": update_data})
        return result.modified_count > 0

    async def delete(self, user_id: str) -> bool:
        result = await self.collection.delete_one({"id": user_id})
        return result.deleted_count > 0


from fastapi import Depends

def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> UserRepository:
    return UserRepository(db)
