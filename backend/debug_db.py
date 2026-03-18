import asyncio
import motor.motor_asyncio

async def debug():
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["college2-main"]
    
    print("--- STUDENTS ---")
    students = await db.students.find({"name": {"$regex": "Sanjay|Dhanush", "$options": "i"}}).to_list(None)
    for s in students:
        print(f"Name: {s.get('name')}, is_active: {s.get('is_active')}, user_id: {s.get('user_id')}")
        
    print("\n--- FEE STRUCTURES ---")
    fees = await db.fee_structures.find({"is_active": True}).to_list(None)
    for f in fees:
        print(f"Name: {f.get('name')}, due_date: {f.get('due_date')}, is_active: {f.get('is_active')}")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(debug())
