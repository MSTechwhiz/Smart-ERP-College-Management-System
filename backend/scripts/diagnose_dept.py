"""Diagnose: check if users exist for non-IT depts but have wrong student dept_id."""
import asyncio, sys, os
sys.path.append(os.getcwd())

async def main():
    try:
        from backend.app.core.database import connect_to_mongo, get_db
    except ImportError:
        from app.core.database import connect_to_mongo, get_db

    await connect_to_mongo()
    db = get_db()

    # Count users per department vs students per department
    depts = await db.departments.find({}, {"_id": 0, "id": 1, "name": 1, "code": 1}).to_list(None)
    print(f"\n{'DEPT':<12} {'USERS':<8} {'STUDENTS':<10} {'STUDENT DEPT OK?'}")
    print("-" * 55)
    for d in sorted(depts, key=lambda x: x.get("code", "")):
        user_count = await db.users.count_documents({"department_id": d["id"], "role": "student"})
        stud_count = await db.students.count_documents({"department_id": d["id"]})
        print(f"{d.get('code','?'):<12} {user_count:<8} {stud_count:<10}")

    # Now look at a sample non-IT user to see their student record
    print("\n--- Sample CSE user + student record ---")
    cse_dept = await db.departments.find_one({"code": "CSE"}, {"_id": 0})
    if cse_dept:
        cse_users = await db.users.find({"department_id": cse_dept["id"], "role": "student"}, {"_id": 0}).to_list(5)
        for u in cse_users[:3]:
            stud = await db.students.find_one({"user_id": u["id"]}, {"_id": 0, "department_id": 1, "year": 1, "roll_number": 1})
            print(f"  User: {u.get('email')} dept_id={u.get('department_id')[:8]}...")
            print(f"  Student: {stud}")
    else:
        print("  CSE dept not found!")

if __name__ == "__main__":
    asyncio.run(main())
