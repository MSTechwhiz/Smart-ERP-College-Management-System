"""Quick DB state check — shows student count per department."""
import asyncio, sys, os
sys.path.append(os.getcwd())

async def main():
    try:
        from backend.app.core.database import connect_to_mongo, get_db
    except ImportError:
        from app.core.database import connect_to_mongo, get_db

    await connect_to_mongo()
    db = get_db()

    # All departments
    depts = await db.departments.find({}, {"_id": 0, "id": 1, "name": 1, "code": 1}).to_list(None)
    print(f"\n{'DEPT':<40} {'CODE':<8} {'STUDENTS'}")
    print("-" * 60)
    total = 0
    for d in sorted(depts, key=lambda x: x.get("name", "")):
        count = await db.students.count_documents({"department_id": d["id"]})
        total += count
        print(f"{d.get('name','?'):<40} {d.get('code','?'):<8} {count}")

    print("-" * 60)
    print(f"{'TOTAL':<48} {total}")

    # Year-wise for each dept
    print("\n\nYear-wise breakdown:")
    for d in sorted(depts, key=lambda x: x.get("name", "")):
        y_counts = {}
        for yr in [1, 2, 3, 4]:
            c = await db.students.count_documents({"department_id": d["id"], "year": yr})
            y_counts[yr] = c
        if sum(y_counts.values()) > 0:
            print(f"  {d.get('code','?')}: Y1={y_counts[1]} Y2={y_counts[2]} Y3={y_counts[3]} Y4={y_counts[4]}")

if __name__ == "__main__":
    asyncio.run(main())
