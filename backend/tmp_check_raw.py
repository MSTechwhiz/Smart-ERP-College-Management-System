
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.academia_erp
    fees = await db.fee_structures.find({}).to_list(None)
    import json
    for f in fees:
        f['_id'] = str(f['_id'])
        print(json.dumps(f))

if __name__ == "__main__":
    asyncio.run(check())
