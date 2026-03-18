import motor.motor_asyncio
import asyncio

async def check():
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["academia_erp"]
    logs = await db.fee_notification_logs.find().to_list(None)
    print(f"Total logs: {len(logs)}")
    for l in logs:
        print(f"Student: {l.get('student_name')}, Fee: {l.get('fee_name')}, Status: {l.get('status')}")
    client.close()

if __name__ == "__main__":
    asyncio.run(check())
