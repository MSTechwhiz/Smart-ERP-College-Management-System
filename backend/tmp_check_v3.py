
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.academia_erp
    
    fees = await db.fee_structures.find({}).to_list(None)
    for f in fees:
        fid = f.get('id')
        name = f.get('name')
        count = await db.fee_payments.count_documents({"fee_structure_id": fid})
        print(f"ID: {fid} | Name: {name} | Payments: {count}")

if __name__ == "__main__":
    asyncio.run(check())
