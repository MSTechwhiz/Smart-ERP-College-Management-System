import asyncio
import os
import sys
import csv
import uuid
from datetime import datetime, timezone
import bcrypt
import subprocess

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

SHEET_BASE_URL = "https://docs.google.com/spreadsheets/d/1WoMDeAP9hRK74bIqmw5ubyfDFfsHKdLn/export?format=csv&gid="
YEARS_CONFIG = [
    {"year": "1", "gid": "87787809", "batch": "2025-2029", "semester": 1, "limit": 10},
    {"year": "2", "gid": "1672764592", "batch": "2024-2028", "semester": 3, "limit": 10},
    {"year": "3", "gid": "901273758", "batch": "2023-2027", "semester": 5, "limit": 10},
    {"year": "4", "gid": "1660521861", "batch": "2022-2026", "semester": 7, "limit": None}, # None means all
]

async def get_db_info():
    try:
        from backend.app.core.database import connect_to_mongo, get_db
    except ImportError:
        from app.core.database import connect_to_mongo, get_db
        
    await connect_to_mongo()
    db = get_db()
    it_dept = await db.departments.find_one({"code": "IT"}, {"id": 1})
    if not it_dept:
        it_dept = await db.departments.find_one({}, {"id": 1})
    admin_user = await db.users.find_one({"role": "admin"}, {"id": 1, "name": 1, "role": 1})
    return db, it_dept["id"], admin_user

async def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

async def download_csv(gid, filename):
    url = f"{SHEET_BASE_URL}{gid}"
    cmd = f"powershell -Command \"Invoke-WebRequest -Uri '{url}' -OutFile '{filename}'\""
    subprocess.run(cmd, shell=True, check=True)

async def process_import():
    db, dept_id, admin_user = await get_db_info()
    overall_success = 0
    overall_error = 0
    
    for config in YEARS_CONFIG:
        print(f"\nProcessing Year {config['year']}...")
        csv_path = f"backend/scripts/import_y{config['year']}.csv"
        await download_csv(config['gid'], csv_path)
        
        students_to_import = []
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            found_header = False
            count = 0
            for row in reader:
                if not row or all(not cell.strip() for cell in row): continue
                if "S.NO" in row[0]:
                    found_header = True
                    continue
                if found_header and row[0].isdigit():
                    students_to_import.append(row)
                    count += 1
                    if config['limit'] and count >= config['limit']:
                        break
        
        print(f"Found {len(students_to_import)} students for Year {config['year']}.")
        
        for student_data in students_to_import:
            try:
                name = student_data[1].strip()
                reg_num = student_data[2].strip()
                email = student_data[6].strip()
                
                # Check unique constraints
                existing_user = await db.users.find_one({"email": email})
                if existing_user:
                    print(f"  Skipping duplicate email: {email}")
                    continue
                existing_student = await db.students.find_one({"register_number": reg_num})
                if existing_student:
                    print(f"  Skipping duplicate register number: {reg_num}")
                    continue

                clean_name = name.replace(" ", "")
                hashed_pwd = await hash_password(f"{clean_name}@123")
                
                user_id = str(uuid.uuid4())
                user_doc = {
                    "id": user_id, "email": email, "name": name, "password": hashed_pwd,
                    "role": "student", "department_id": dept_id, "permissions": [],
                    "sub_roles": [], "is_active": True, "created_at": datetime.now(timezone.utc).isoformat()
                }
                await db.users.insert_one(user_doc)
                
                student_id = str(uuid.uuid4())
                student_doc = {
                    "id": student_id, "user_id": user_id, "roll_number": reg_num,
                    "register_number": reg_num, "department_id": dept_id,
                    "batch": config['batch'], "year": int(config['year']),
                    "semester": config['semester'], "section": "A",
                    "date_of_birth": student_data[4] if len(student_data) > 4 else None,
                    "gender": student_data[3] if len(student_data) > 3 else None,
                    "blood_group": student_data[7] if len(student_data) > 7 else None,
                    "mobile_number": student_data[5] if len(student_data) > 5 else None,
                    "email": email,
                    "community": student_data[10] if len(student_data) > 10 else None,
                    "umis_id": student_data[9] if len(student_data) > 9 else None,
                    "aadhar_number": student_data[8] if len(student_data) > 8 else None,
                    "admission_quota": student_data[11] if len(student_data) > 11 else None,
                    "cgpa": 8.0, "is_active": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "created_by": admin_user["id"]
                }
                await db.students.insert_one(student_doc)
                overall_success += 1
            except Exception as e:
                print(f"  Error importing student {student_data[1]}: {str(e)}")
                overall_error += 1
                
    print(f"\nFinal Import Result: {overall_success} succeeded, {overall_error} failed.")

if __name__ == "__main__":
    asyncio.run(process_import())
