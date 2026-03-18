"""
Cleanup: remove fake/demo student records and their users.
Fake students are identified by:
  1. Email ending in @academia.edu (demo accounts)
  2. Any student whose register_number is 'REG...' (generated placeholder, not from sheet)
     AND has a @academia.edu email
"""
import asyncio, sys, os
sys.path.append(os.getcwd())

DEMO_EMAIL_DOMAINS = ["@academia.edu"]
DEMO_REGISTER_PATTERN = "REG"   # Only if ALSO has demo email

async def main():
    try:
        from backend.app.core.database import connect_to_mongo, get_db
    except ImportError:
        from app.core.database import connect_to_mongo, get_db

    await connect_to_mongo()
    db = get_db()

    # Find demo users (student role with academia.edu email)
    # USER REQUEST: Except Rahul Verma, remove all demo data.
    demo_users = await db.users.find({
        "role": "student",
        "email": {"$regex": "@academia\\.edu$", "$options": "i"},
        "name": {"$ne": "Rahul Verma"}  # Keep Rahul Verma
    }, {"_id": 0, "id": 1, "email": 1, "name": 1}).to_list(None)

    print(f"Found {len(demo_users)} demo student user(s):")
    demo_user_ids = []
    for u in demo_users:
        print(f"  - {u.get('name')} <{u.get('email')}>")
        demo_user_ids.append(u["id"])

    # Delete their student records
    stud_deleted = 0
    for uid in demo_user_ids:
        result = await db.students.delete_many({"user_id": uid})
        stud_deleted += result.deleted_count

    # Delete the demo users themselves
    user_deleted = 0
    if demo_user_ids:
        result = await db.users.delete_many({"id": {"$in": demo_user_ids}})
        user_deleted = result.deleted_count

    print(f"\nDeleted {stud_deleted} student records and {user_deleted} user records.")

    # Also clean up any orphaned students with no user
    all_student_user_ids = {s["user_id"] async for s in db.students.find({}, {"_id": 0, "user_id": 1})}
    all_user_ids = {u["id"] async for u in db.users.find({"role": "student"}, {"_id": 0, "id": 1})}
    orphaned_ids = all_student_user_ids - all_user_ids
    if orphaned_ids:
        result = await db.students.delete_many({"user_id": {"$in": list(orphaned_ids)}})
        print(f"Cleaned up {result.deleted_count} orphaned student records.")

    # Final count
    total = await db.students.count_documents({})
    print(f"\nRemaining students in DB: {total}")

if __name__ == "__main__":
    asyncio.run(main())
