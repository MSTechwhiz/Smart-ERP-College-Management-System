"""
Full Department Student Sync — AcademiaOS
Imports ALL students from Google Sheet with these rules:
  - ALL years: No limits
  - No duplicates: matched primarily by Register Number
  - Passwords: FirstName@123
  - Columns: Import ALL columns (Admission Quota, EMIS/UMIS, Parent info, etc.)
"""

import asyncio, os, sys, csv, uuid, datetime, httpx, re
from typing import Dict, Optional

sys.path.append(os.getcwd())

# ─── Google Sheet GIDs (Verified) ─────────────────────────────────────────────
SHEET_TABS = [
    {"name": "IT I YEAR",    "gid": "0",          "dept": "Information Technology",    "code": "IT",    "year": 1, "sem": 1},
    {"name": "IT II YEAR",   "gid": "1672764592", "dept": "Information Technology",    "code": "IT",    "year": 2, "sem": 3},
    {"name": "IT-III YEAR",  "gid": "901273758",  "dept": "Information Technology",    "code": "IT",    "year": 3, "sem": 5},
    {"name": "IT- IV YEAR",  "gid": "1660521861", "dept": "Information Technology",    "code": "IT",    "year": 4, "sem": 7},
    
    {"name": "CSE- I YEAR",  "gid": "159215229",  "dept": "Computer Science",          "code": "CSE",   "year": 1, "sem": 1},
    {"name": "CSE II YEAR",  "gid": "195936912",  "dept": "Computer Science",          "code": "CSE",   "year": 2, "sem": 3},
    {"name": "CSE-III YEAR", "gid": "309077697",  "dept": "Computer Science",          "code": "CSE",   "year": 3, "sem": 5},
    {"name": "CSE-IV YEAR",  "gid": "1878153636", "dept": "Computer Science",          "code": "CSE",   "year": 4, "sem": 7},
    
    {"name": "ECE I YEAR",   "gid": "1642591953", "dept": "Electronics and Communication", "code": "ECE", "year": 1, "sem": 1},
    {"name": "ECE II YEAR",  "gid": "2074526952", "dept": "Electronics and Communication", "code": "ECE", "year": 2, "sem": 3},
    {"name": "ECE III YEAR", "gid": "203265",      "dept": "Electronics and Communication", "code": "ECE", "year": 3, "sem": 5},
    {"name": "ECE IV YEAR",  "gid": "1225022765", "dept": "Electronics and Communication", "code": "ECE", "year": 4, "sem": 7},
    
    {"name": "AIDS- I YEAR", "gid": "1556604102", "dept": "Artificial Intelligence and Data Science", "code": "AIDS", "year": 1, "sem": 1},
    {"name": "AIDS II YEAR", "gid": "1954292265", "dept": "Artificial Intelligence and Data Science", "code": "AIDS", "year": 2, "sem": 3},
    
    {"name": "CSBS I YEAR",  "gid": "906769156",  "dept": "Computer Science and Business Systems", "code": "CSBS", "year": 1, "sem": 1},
    {"name": "CSBS II YEAR", "gid": "1448247822", "dept": "Computer Science and Business Systems", "code": "CSBS", "year": 2, "sem": 3},
    
    {"name": "EEE IV YEAR",  "gid": "1451372023", "dept": "Electrical and Electronics", "code": "EEE", "year": 4, "sem": 7},
]

BASE_URL = "https://docs.google.com/spreadsheets/d/1WoMDeAP9hRK74bIqmw5ubyfDFfsHKdLn/export?format=csv&gid="

# ─── DB helpers ───────────────────────────────────────────────────────────────
async def get_deps():
    try:
        from backend.app.core.database import connect_to_mongo, get_db
        from backend.app.core.security import hash_password
    except ImportError:
        from app.core.database import connect_to_mongo, get_db
        from app.core.security import hash_password

    await connect_to_mongo()
    db = get_db()
    return db, hash_password


async def get_or_create_dept(db, name: str, code: str) -> str:
    dept = await db.departments.find_one({
        "$or": [{"code": code}, {"name": name}]
    }, {"_id": 0})
    
    if not dept:
        dept_id = str(uuid.uuid4())
        doc = {
            "id": dept_id, "name": name, "code": code,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        await db.departments.insert_one(doc)
        print(f"  [+] Created department: {name} ({code})")
        return dept_id
    
    return dept["id"]


async def download_tab(gid: str, path: str) -> bool:
    # gid=0 often fails with 400 in direct export link; no gid works for first sheet
    url = f"{BASE_URL}{gid}" if gid != "0" else "https://docs.google.com/spreadsheets/d/1WoMDeAP9hRK74bIqmw5ubyfDFfsHKdLn/export?format=csv"
    async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
        for attempt in range(3):
            try:
                r = await client.get(url)
                if r.status_code == 200:
                    with open(path, "wb") as f:
                        f.write(r.content)
                    return True
                else:
                    print(f"    FAIL: {r.status_code} for gid {gid}")
            except Exception as e: 
                print(f"    ERROR: {str(e)}")
            await asyncio.sleep(2)
    return False


def make_password(name: str) -> str:
    clean_name = re.sub(r"[^a-zA-Z]", "", name.strip().split()[0])
    return f"{clean_name}@123" if clean_name else "Student@123"


async def sync_tab(tab: dict, db, hash_password):
    path = f"tmp_sync_{tab['gid']}.csv"
    print(f"\n>>> Tab: {tab['name']} ({tab['dept']})")

    if not await download_tab(tab["gid"], path):
        print(f"    SKIP - download failed")
        return {"new": 0, "updated": 0, "skipped": 0}

    dept_id = await get_or_create_dept(db, tab["dept"], tab["code"])

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        all_lines = f.readlines()

    header_idx = -1
    for i, line in enumerate(all_lines[:15]):
        u = line.upper()
        if "REGISTER" in u and ("NO" in u or "NUMBER" in u):
            header_idx = i
            break

    if header_idx == -1:
        print(f"    SKIP - no header row found.")
        os.remove(path)
        return {"new": 0, "updated": 0, "skipped": 0}

    reader = csv.DictReader(all_lines[header_idx:])
    count_new = count_updated = count_skipped = 0

    def normalize_quota(val: str) -> str:
        if not val: return "GQ"
        v = str(val).upper().strip()
        if v in ["MQ", "MANAGEMENT"]: return "Management"
        if v in ["FG", "FG QUOTA"]: return "FG"
        if "PMSS" in v: return "PMSS"
        if "7.5" in v: return "7.5 Quota"
        if v in ["GQ", "GOVERNMENT", "GOVERNMENT QUOTA"]: return "Government"
        return val.strip()

    for row in reader:
        # Normalize keys
        rn = {k.strip().upper(): (v.strip() if v else "") for k, v in row.items() if k}

        name = next((v for k, v in rn.items() if "NAME" in k and "STUDENT" in k), rn.get("NAME OF THE STUDENTS", rn.get("NAME")))
        if not name or name.upper() in ["NAME", "NIL", "NA", ""]: continue

        reg_no = next((v for k, v in rn.items() if "REGISTER" in k and ("NO" in k or "NUMBER" in k)), None)
        if not reg_no or reg_no.upper() in ["NIL", "NA", ""]:
            count_skipped += 1
            continue

        email = next((v for k, v in rn.items() if "MAIL" in k or "EMAIL" in k), "")
        if not email or "@" not in email:
            email = f"{re.sub(r'[^a-zA-Z0-9]', '', name).lower()}{reg_no[-4:] or 'stud'}@sbc.edu"
        else:
            email = email.lower().strip()

        # Step 4: Map Columns to Student Schema
        aadhar      = next((v for k, v in rn.items() if "AADHAR" in k or "ADHAR" in k), "")
        umis_id     = next((v for k, v in rn.items() if "UMIS" in k), "")
        gender      = next((v for k, v in rn.items() if "GENDER" in k), "MALE")
        dob         = next((v for k, v in rn.items() if "BIRTH" in k), "")
        blood_group = next((v for k, v in rn.items() if "BLOOD" in k), "")
        mobile      = next((v for k, v in rn.items() if "STUDENT MOBILE" in k), "")
        address     = next((v for k, v in rn.items() if "ADDRESS" in k), "")
        community   = next((v for k, v in rn.items() if "COMMUNITY" in k), "")
        quota       = next((v for k, v in rn.items() if "QUOTA" in k or "ADMISSION CATEGORY" in k or "ADMISSION QUOTA" in k), "")
        p_name      = next((v for k, v in rn.items() if "PARENT NAME" in k or "PARENTS NAME" in k or "FATHER" in k), "")
        p_mobile    = next((v for k, v in rn.items() if "PARENT CONTACT" in k or "PARENT MOBILE" in k or "PARENT CONTACT NUMBER" in k), "")
        p_mail      = next((v for k, v in rn.items() if "PARENT MAIL" in k), "")
        placement   = next((v for k, v in rn.items() if "PLACEMENT" in k), "")
        
        student_data = {
            "register_number": reg_no,
            "roll_number":     reg_no,
            "department_id":   dept_id,
            "batch":           f"{2024 - tab['year'] + 1}-{2024 - tab['year'] + 5}",
            "year":            tab["year"],
            "semester":        tab["sem"],
            "section":         rn.get("SECTION", "A") or "A",
            "community":       community,
            "blood_group":     blood_group,
            "gender":          gender,
            "date_of_birth":   dob,
            "mobile_number":   mobile,
            "permanent_address": address,
            "aadhar_number":   aadhar,
            "umis_id":         umis_id,
            "admission_quota": normalize_quota(quota),
            "parent_name":     p_name,
            "parent_phone":    p_mobile,
            "parent_details": {
                "father_name":    p_name,
                "father_contact": p_mobile,
                "father_email":   p_mail,
                "mother_name": "", "mother_contact": ""
            },
            "placement_details": placement,
            "is_active":   True,
            "updated_at":  datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        # Match primarily by Register Number
        existing_student = await db.students.find_one({"register_number": reg_no}, {"_id": 0})
        if not existing_student:
            existing_student = await db.students.find_one({"roll_number": reg_no}, {"_id": 0})

        if existing_student:
            await db.students.update_one({"id": existing_student["id"]}, {"$set": student_data})
            await db.users.update_one({"id": existing_student["user_id"]}, {"$set": {"name": name, "department_id": dept_id}})
            count_updated += 1
        else:
            existing_user = await db.users.find_one({"email": email}, {"_id": 0})
            if existing_user:
                uid = existing_user["id"]
                await db.users.update_one({"id": uid}, {"$set": {"name": name, "role": "student", "department_id": dept_id}})
            else:
                uid = str(uuid.uuid4())
                hashed_pw = await hash_password(make_password(name))
                user_doc = {
                    "id": uid, "name": name, "email": email,
                    "password": hashed_pw,
                    "role": "student", "department_id": dept_id,
                    "is_active": True,
                    "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }
                await db.users.insert_one(user_doc)
            
            student_data.update({"id": str(uuid.uuid4()), "user_id": uid})
            await db.students.insert_one(student_data)
            count_new += 1

    if os.path.exists(path): os.remove(path)
    print(f"    Result -> New: {count_new}, Updated: {count_updated}, Skipped: {count_skipped}")
    return {"new": count_new, "updated": count_updated, "skipped": count_skipped}


async def main():
    db, hash_password = await get_deps()
    total_new = total_updated = 0
    print(f"Starting FULL ADVANCED sync - {len(SHEET_TABS)} tabs\n{'='*70}")
    for tab in SHEET_TABS:
        result = await sync_tab(tab, db, hash_password)
        total_new += result["new"]
        total_updated += result["updated"]
    print(f"\n{'='*70}")
    print(f"SYNC COMPLETE - Total New: {total_new}, Total Updated: {total_updated}")

if __name__ == "__main__":
    asyncio.run(main())
