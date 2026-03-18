import asyncio
import os
import sys

# Add directory to path
sys.path.append(os.getcwd())

async def main():
    try:
        from backend.app.core.database import connect_to_mongo, get_db
    except ImportError:
        from app.core.database import connect_to_mongo, get_db

    await connect_to_mongo()
    db = get_db()
    
    email = 'kiruthigahar70208627@gmail.com'
    print(f"Checking for email: {email}")
    
    user = await db.users.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}})
    if user:
        print(f"User found: {user['id']} | Email in DB: '{user['email']}'")
    else:
        print("User not found via exact regex")
        
    print("\nFuzzy check (containing string):")
    async for u in db.users.find({"email": {"$regex": "kiruthigahar70208627"}}):
        print(f"Fuzzy match: {u['id']} | Email in DB: '{u['email']}'")

    roll = '512724205038'
    print(f"\nChecking for roll number: {roll}")
    student = await db.students.find_one({"roll_number": roll})
    if student:
        print(f"Student found: {student['id']} | User ID: {student['user_id']}")
    else:
        print("Student not found")

if __name__ == "__main__":
    asyncio.run(main())
