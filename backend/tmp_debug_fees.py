
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json

async def check():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.academia_erp
    
    fees = await db.fee_structures.find({}).to_list(None)
    payments = await db.fee_payments.find({}).to_list(None)
    
    pay_counts = {}
    for p in payments:
        fid = p.get('fee_structure_id')
        pay_counts[fid] = pay_counts.get(fid, 0) + 1
        
    print("--- FEE STRUCTURES ---")
    for f in fees:
        fid = f.get('id')
        name = f.get('name')
        count = pay_counts.get(fid, 0)
        print(f"ID: {fid} | Name: {name} | Payments: {count}")
    print("----------------------")

if __name__ == "__main__":
    asyncio.run(check())
