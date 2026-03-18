import asyncio
import motor.motor_asyncio
from datetime import datetime, timezone, timedelta

async def check():
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["college2-main"]
    f = await db.fee_structures.find_one({"name": "Final Year Verification Fee"})
    if f:
        print(f"Type: {type(f.get('due_date'))}, Value: |{f.get('due_date')}|")
        
        # Test query
        now = datetime.now(timezone.utc)
        today_str = now.strftime("%Y-%m-%d")
        tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        relevant_dates = [today_str, tomorrow_str]
        
        print(f"Searching for: {relevant_dates}")
        match = await db.fee_structures.find({"due_date": {"$in": relevant_dates}}).to_list(None)
        print(f"Matches found: {len(match)}")
    else:
        print("Fee not found")
    client.close()

if __name__ == "__main__":
    asyncio.run(check())
