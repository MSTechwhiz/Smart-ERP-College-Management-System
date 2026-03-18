
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.academia_erp
    fees = await db.fee_structures.find({}, {"name": 1, "id": 1, "_id": 1}).to_list(None)
    print("-" * 50)
    for f in fees:
        print(f"Name: {f.get('name', 'N/A'):<25} | ID: {f.get('id', 'N/A'):<36} | _ID: {str(f['_id'])}")
    print("-" * 50)

if __name__ == "__main__":
    asyncio.run(check())
