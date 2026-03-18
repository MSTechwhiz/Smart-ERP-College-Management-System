
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    dbs = await client.list_database_names()
    print(f"Databases: {dbs}")

if __name__ == "__main__":
    asyncio.run(check())
