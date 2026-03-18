"""
Verification Script — Student Distribution
Shows counts per Dept, Year, and Admission Quota.
"""
import asyncio, os, sys
from collections import Counter

sys.path.append(os.getcwd())

async def main():
    try:
        from backend.app.core.database import connect_to_mongo, get_db
    except ImportError:
        from app.core.database import connect_to_mongo, get_db
        
    await connect_to_mongo()
    db = get_db()
    
    students = await db.students.find({}, {
        "department_id": 1, "year": 1, "admission_quota": 1, "register_number": 1
    }).to_list(None)
    
    print(f"Total Students in DB: {len(students)}")
    
    # Dept counts
    dept_ids = [s["department_id"] for s in students]
    dept_counts = Counter(dept_ids)
    
    print("\nCounts by Department:")
    for d_id, count in dept_counts.items():
        dept = await db.departments.find_one({"id": d_id})
        name = dept["name"] if dept else "Unknown"
        print(f"  {name:45}: {count}")
        
    # Year counts
    year_counts = Counter([s.get("year", 1) for s in students])
    print("\nCounts by Year:")
    for yr in sorted(year_counts.keys()):
        print(f"  Year {yr}: {year_counts[yr]}")
        
    # Quota counts
    quota_counts = Counter([s.get("admission_quota", "N/A") for s in students])
    print("\nCounts by Admission Category (Quota):")
    for q, count in quota_counts.items():
        print(f"  {str(q):30}: {count}")

if __name__ == "__main__":
    asyncio.run(main())
