from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone

class CommunicationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.communications

    async def create(self, comm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new communication record"""
        result = await self.collection.insert_one(comm_data)
        return await self.collection.find_one({"_id": result.inserted_id}, {"_id": 0})

    async def get_by_id(self, comm_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific communication by its ID"""
        return await self.collection.find_one({"id": comm_id, "is_deleted": False}, {"_id": 0})

    async def get_received_by_role(self, role: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch communications targeted to a specific role"""
        query = {"target_role": role, "is_deleted": False}
        docs = await self.collection.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        return docs

    async def get_sent_by_user(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch communications sent by a specific user"""
        query = {"sender_id": user_id, "is_deleted": False}
        docs = await self.collection.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        return docs

    async def mark_as_read(self, comm_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Add user_id to read_status array if not already present"""
        await self.collection.update_one(
            {"id": comm_id},
            {"$addToSet": {"read_status": user_id}}
        )
        return await self.get_by_id(comm_id)
        
    async def delete(self, comm_id: str) -> bool:
        """Soft delete a communication"""
        result = await self.collection.update_one(
            {"id": comm_id},
            {"$set": {"is_deleted": True, "deleted_at": datetime.now(timezone.utc).isoformat()}}
        )
        return result.modified_count > 0

def get_communication_repository(db: AsyncIOMotorDatabase) -> CommunicationRepository:
    return CommunicationRepository(db)
