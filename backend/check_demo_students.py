import asyncio
import motor.motor_asyncio

async def check_demo_students():
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["academia_erp"]
    
    mobiles = ["8667781655", "8838216441"]
    names = ["Sanjay", "Dhanush", "Sanjay M", "J Dhanush"]
    
    print("--- Searching by Mobile ---")
    s_mob = await db.students.find({"mobile_number": {"$in": mobiles}}).to_list(None)
    for s in s_mob:
        print(f"Name: {s.get('name')}, Mobile: {s.get('mobile_number')}, Dept: {s.get('department_id')}, Batch: {s.get('batch')}")

    print("\n--- Searching by Name ---")
    s_name = await db.students.find({"name": {"$in": names}}).to_list(None)
    for s in s_name:
        print(f"Name: {s.get('name')}, Mobile: {s.get('mobile_number')}, Dept: {s.get('department_id')}, Batch: {s.get('batch')}")

    client.close()

if __name__ == "__main__":
    asyncio.run(check_demo_students())
