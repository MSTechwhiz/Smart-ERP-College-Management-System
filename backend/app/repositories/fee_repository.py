from __future__ import annotations

from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..core.database import get_db
from fastapi import Depends

class FeeRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create_structure(self, doc: Dict[str, Any]) -> str:
        await self.db.fee_structures.insert_one(doc)
        doc.pop("_id", None)
        return doc["id"]

    async def get_structures(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.db.fee_structures.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(None)

    async def get_structure_by_id(self, fee_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.fee_structures.find_one({"id": fee_id}, {"_id": 0})

    async def update_structure(self, fee_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.db.fee_structures.update_one({"id": fee_id}, {"$set": update_data})
        return result.modified_count > 0

    async def delete_structure(self, fee_id: str) -> bool:
        result = await self.db.fee_structures.delete_one({"id": fee_id})
        return result.deleted_count > 0

    async def create_payment(self, doc: Dict[str, Any]) -> str:
        await self.db.fee_payments.insert_one(doc)
        doc.pop("_id", None)
        return doc["id"]

    async def get_payment_by_id(self, payment_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.fee_payments.find_one({"id": payment_id}, {"_id": 0})

    async def update_payment(self, payment_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.db.fee_payments.update_one({"id": payment_id}, {"$set": update_data})
        return result.modified_count > 0

    async def get_payments(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.db.fee_payments.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(None)

    async def count_payments(self, query: Dict[str, Any]) -> int:
        return await self.db.fee_payments.count_documents(query)

def get_fee_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> FeeRepository:
    return FeeRepository(db)
