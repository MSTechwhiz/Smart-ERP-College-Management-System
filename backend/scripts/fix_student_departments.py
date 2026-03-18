"""
Re-assign each student's department_id from their linked user's department_id.
This fixes the case where students were imported with the wrong department.
Also assigns year from user's register_number pattern if possible.
"""
import asyncio, sys, os
sys.path.append(os.getcwd())

async def main():
    try:
        from backend.app.core.database import connect_to_mongo, get_db
    except ImportError:
        from app.core.database import connect_to_mongo, get_db

    await connect_to_mongo()
    db = get_db()

    students = await db.students.find({}, {"_id": 0, "id": 1, "user_id": 1, "department_id": 1}).to_list(None)
    print(f"Total students: {len(students)}")

    fixed = 0
    for s in students:
        user = await db.users.find_one({"id": s["user_id"]}, {"_id": 0, "department_id": 1})
        if not user:
            continue
        user_dept = user.get("department_id")
        if user_dept and user_dept != s.get("department_id"):
            await db.students.update_one({"id": s["id"]}, {"$set": {"department_id": user_dept}})
            fixed += 1

    print(f"Re-assigned {fixed} student records to correct department.")

    # Final counts
    depts = await db.departments.find({}, {"_id": 0, "id": 1, "name": 1, "code": 1}).to_list(None)
    print(f"\n{'CODE':<8} {'STUDENTS'}")
    for d in sorted(depts, key=lambda x: x.get("code", "")):
        c = await db.students.count_documents({"department_id": d["id"]})
        if c > 0:
            print(f"  {d['code']:<8} {c}")

if __name__ == "__main__":
    asyncio.run(main())
