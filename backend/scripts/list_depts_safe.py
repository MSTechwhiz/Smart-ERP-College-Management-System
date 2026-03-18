import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.app.core.database import connect_to_mongo, get_db

async def list_depts():
    await connect_to_mongo()
    db = get_db()
    depts = await db.departments.find({}, {"_id": 0}).to_list(None)
    for d in depts:
        print(f"{d['code']}: {d['id']}")

if __name__ == "__main__":
    asyncio.run(list_depts())
