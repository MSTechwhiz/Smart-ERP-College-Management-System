import asyncio
import os
import httpx
from motor.motor_asyncio import AsyncIOMotorClient

async def test_api():
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", ".env"))
    
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from app.core.config import get_settings
    
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongo_url)
    db = client[settings.db_name]
    
    # Try to find a principal user
    principal = await db.users.find_one({"email": "principal@academia.edu"})
    if not principal:
        principal = await db.users.find_one({"role": "principal"})
    if not principal:
        print("No principal found!")
        return
        
    print(f"Found principal: {principal['email']}")
    
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from app.core.security import create_token
    
    token = create_token(principal)
    
    # 2. GET /api/analytics/risks
    async with httpx.AsyncClient() as hc:
        risks_resp = await hc.get("http://localhost:8000/api/analytics/risks", headers={
            "Authorization": f"Bearer {token}"
        })
        print("Risks Status:", risks_resp.status_code)
        print("Risks Body:", risks_resp.text)

if __name__ == "__main__":
    asyncio.run(test_api())
