
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def check():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.academia_erp
    users = await db.users.find({}, {"name": 1, "role": 1, "id": 1, "email": 1}).to_list(None)
    print("-" * 80)
    print(f"{'Name':<25} | {'Role':<10} | {'Email':<30}")
    print("-" * 80)
    for u in users:
        print(f"{u.get('name', 'N/A'):<25} | {u.get('role', 'N/A'):<10} | {u.get('email', 'N/A'):<30}")
    print("-" * 80)

if __name__ == "__main__":
    asyncio.run(check())
