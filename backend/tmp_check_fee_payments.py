
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.academia_erp
    fees = await db.fee_structures.find({}, {"name": 1, "id": 1}).to_list(None)
    payments = await db.fee_payments.find({}, {"fee_structure_id": 1}).to_list(None)
    
    payment_map = {}
    for p in payments:
        fid = p.get("fee_structure_id")
        payment_map[fid] = payment_map.get(fid, 0) + 1
    
    print("-" * 60)
    print(f"{'Name':<30} | {'ID':<30} | {'Payments':<10}")
    print("-" * 60)
    for f in fees:
        fid = f.get("id")
        pcount = payment_map.get(fid, 0)
        print(f"{f.get('name', 'N/A'):<30} | {fid:<30} | {pcount:<10}")
    print("-" * 60)

if __name__ == "__main__":
    asyncio.run(check())
