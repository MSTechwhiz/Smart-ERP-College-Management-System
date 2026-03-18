"""
Aggressive Student Cleanup — AcademiaOS
1. Downloads all Google Sheet tabs.
2. Identifies all valid Register Numbers.
3. Deletes any student (and their user) NOT in the sheet.
4. Spares "Rahul Verma".
"""

import asyncio, os, sys, csv, httpx, re
from typing import Set

sys.path.append(os.getcwd())

# ─── Google Sheet GIDs ────────────────────────────────────────────────────────
SHEET_TABS = [
    {"gid": "87787809",   "name": "IT I"},
    {"gid": "1672764592", "name": "IT II"},
    {"gid": "901273758",  "name": "IT III"},
    {"gid": "1660521861", "name": "IT IV"},
    {"gid": "159215229",  "name": "CSE I"},
    {"gid": "195936912",  "name": "CSE II"},
    {"gid": "309077697",  "name": "CSE III"},
    {"gid": "1878153636", "name": "CSE IV"},
    {"gid": "1642591953", "name": "ECE I"},
    {"gid": "2074526952", "name": "ECE II"},
    {"gid": "203265",      "name": "ECE III"},
    {"gid": "1225022765", "name": "ECE IV"},
    {"gid": "1556604102", "name": "AIDS I"},
    {"gid": "1954292265", "name": "AIDS II"},
    {"gid": "906769156",  "name": "CSBS I"},
    {"gid": "1448247822", "name": "CSBS II"},
    {"gid": "1451372023", "name": "EEE IV"},
    {"gid": "1931327170", "name": "MECH IV"},
]

BASE_URL = "https://docs.google.com/spreadsheets/d/1WoMDeAP9hRK74bIqmw5ubyfDFfsHKdLn/export?format=csv&gid="

async def download_csv(gid: str) -> str:
    url = f"{BASE_URL}{gid}"
    async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
        r = await client.get(url)
        return r.text if r.status_code == 200 else ""

async def get_valid_register_numbers() -> Set[str]:
    valid_regs = set()
    print(f"Collecting valid register numbers from {len(SHEET_TABS)} tabs...")
    
    for tab in SHEET_TABS:
        csv_text = await download_csv(tab["gid"])
        if not csv_text:
            print(f"  [-] Failed to download tab: {tab['name']}")
            continue
            
        lines = csv_text.splitlines()
        header_idx = -1
        for i, line in enumerate(lines[:15]):
            if "REGISTER" in line.upper() and ("NO" in line.upper() or "NUMBER" in line.upper()):
                header_idx = i
                break
        
        if header_idx == -1:
            print(f"  [-] Header not found in tab: {tab['name']}")
            continue
            
        reader = csv.DictReader(lines[header_idx:])
        count = 0
        for row in reader:
            # Clean keys
            row = {k.strip().upper() if k else "": v.strip() if v else "" for k, v in row.items()}
            reg_no = next((v for k, v in row.items() if "REGISTER" in k and ("NO" in k or "NUMBER" in k)), None)
            
            if reg_no and reg_no.upper() not in ["NIL", "NA", ""]:
                valid_regs.add(reg_no)
                count += 1
        print(f"  [+] Tab {tab['name']}: Found {count} valid students")
        
    return valid_regs

async def main():
    try:
        from backend.app.core.database import connect_to_mongo, get_db
    except ImportError:
        from app.core.database import connect_to_mongo, get_db
        
    await connect_to_mongo()
    db = get_db()
    
    valid_regs = await get_valid_register_numbers()
    if not valid_regs:
        print("CRITICAL: No valid register numbers found. Aborting cleanup to prevent data loss.")
        return
        
    print(f"\nTotal valid Register Numbers found: {len(valid_regs)}")
    
    # Identify students to delete
    cursor = db.students.find({}, {"id": 1, "user_id": 1, "register_number": 1, "roll_number": 1})
    students = await cursor.to_list(None)
    
    to_delete_student_ids = []
    to_delete_user_ids = []
    
    for s in students:
        reg = s.get("register_number") or s.get("roll_number")
        
        # SPARE RAHUL VERMA
        if s.get("roll_number") == "21IT001" or s.get("register_number") == "21IT001":
            # Assuming Rahul Verma's roll is 21IT001 (based on previous logs)
            # But let's check name too if possible
            user = await db.users.find_one({"id": s["user_id"]}, {"name": 1})
            if user and user.get("name") == "Rahul Verma":
                print(f"  [S] Sparing Rahul Verma ({reg})")
                continue
        
        if reg not in valid_regs:
            to_delete_student_ids.append(s["id"])
            to_delete_user_ids.append(s["user_id"])
            print(f"  [-] Marking for deletion: {reg}")

    if not to_delete_student_ids:
        print("\nNo dummy records found that aren't in the sheet.")
    else:
        print(f"\nProceeding to delete {len(to_delete_student_ids)} student records and associated users...")
        
        # Delete students
        res1 = await db.students.delete_many({"id": {"$in": to_delete_student_ids}})
        # Delete users
        res2 = await db.users.delete_many({"id": {"$in": to_delete_user_ids}, "role": "student"})
        
        print(f"  [x] Deleted {res1.deleted_count} student records.")
        print(f"  [x] Deleted {res2.deleted_count} user records.")

    # Cleanup any users with role 'student' that have no student record (orphans)
    # (Except Rahul Verma etc.)
    all_student_user_ids = await db.students.distinct("user_id")
    orphans = await db.users.find({
        "role": "student", 
        "id": {"$nin": all_student_user_ids},
        "name": {"$ne": "Rahul Verma"}
    }, {"id": 1, "email": 1}).to_list(None)
    
    if orphans:
        print(f"\nFound {len(orphans)} orphan student users. Deleting...")
        orphan_ids = [o["id"] for o in orphans]
        res3 = await db.users.delete_many({"id": {"$in": orphan_ids}})
        print(f"  [x] Deleted {res3.deleted_count} orphan users.")

    print("\nCleanup Complete.")

if __name__ == "__main__":
    asyncio.run(main())
