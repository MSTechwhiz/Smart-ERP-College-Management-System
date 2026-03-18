
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.academia_erp
    collections = await db.list_collection_names()
    print(f"Collections: {collections}")
    for c in collections:
        count = await db[c].count_documents({})
        print(f" - {c}: {count}")

if __name__ == "__main__":
    asyncio.run(check())
