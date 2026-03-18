from __future__ import annotations
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..core.database import get_db
from fastapi import Depends

class CounterRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.counters

    async def get_next_sequence(self, counter_id: str) -> int:
        """Atomic increment and return of sequence number"""
        result = await self.collection.find_one_and_update(
            {"_id": counter_id},
            {"$inc": {"value": 1}},
            upsert=True,
            return_document=True
        )
        return result["value"]

def get_counter_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> CounterRepository:
    return CounterRepository(db)
