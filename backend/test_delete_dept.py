import asyncio
import httpx
import sys, os

# Setup path and env
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", ".env"))

from app.core.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.security import create_token

async def test_admin_delete_dept():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongo_url)
    db = client[settings.db_name]
    
    # Get an admin user
    admin = await db.users.find_one({"role": "admin"})
    if not admin:
        print("No admin user found.")
        return
        
    token = create_token(admin)
    print("Admin Token Generated.")
    
    # 1. Let's create a dummy isolated department
    import uuid
    dummy_dept_id = str(uuid.uuid4())
    await db.departments.insert_one({
        "id": dummy_dept_id,
        "name": "Dummy Test Dept",
        "code": "DTD",
        "created_at": "2024-01-01T00:00:00",
        "created_by": admin["id"]
    })
    
    # 2. Delete it using API
    async with httpx.AsyncClient() as hc:
        # Delete isolated department (Should return 200 OK)
        resp1 = await hc.delete(f"http://localhost:8000/api/departments/{dummy_dept_id}", headers={
            "Authorization": f"Bearer {token}"
        })
        print("Isolated Department Delete Status:", resp1.status_code)
        print("Isolated Department Delete Body:", resp1.json())
        
        # 3. Find a department with students/faculty
        dept_with_users = await db.departments.find_one({})
        if dept_with_users:
            dept_id = dept_with_users["id"]
            # Delete associated department (Should return 400 Bad Request, NOT 403)
            resp2 = await hc.delete(f"http://localhost:8000/api/departments/{dept_id}", headers={
                "Authorization": f"Bearer {token}"
            })
            print("Associated Department Delete Status:", resp2.status_code)
            print("Associated Department Delete Body:", resp2.json())

if __name__ == "__main__":
    asyncio.run(test_admin_delete_dept())
