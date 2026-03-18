import asyncio
import os
import sys
import csv
import uuid
from datetime import datetime, timezone
import bcrypt

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

async def get_db_info():
    try:
        from backend.app.core.database import connect_to_mongo, get_db
    except ImportError:
        from app.core.database import connect_to_mongo, get_db
        
    await connect_to_mongo()
    db = get_db()
    
    # Get IT department
    it_dept = await db.departments.find_one({"code": "IT"}, {"id": 1})
    if not it_dept:
        # Fallback to FIRST department if IT doesn't exist (safety)
        it_dept = await db.departments.find_one({}, {"id": 1})
        
    # Get an admin user for audit log
    admin_user = await db.users.find_one({"role": "admin"}, {"id": 1, "name": 1, "role": 1})
    
    return db, it_dept["id"], admin_user

async def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

async def import_students():
    db, dept_id, admin_user = await get_db_info()
    csv_path = "backend/scripts/students_import.csv"
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    students_to_import = []
    
    # Year mapping and semester mapping logic
    # 1st Year: Index 0-9 (first 10) -> Semester 1
    # 2nd Year: Index 0-9 (first 10) -> Semester 3
    # 3rd Year: Index 0-9 (first 10) -> Semester 5
    # 4th Year: ALL -> Semester 7
    
    # We need to detect sections in the CSV. 
    # Based on research, the CSV has headers like "STUDENT DETAILS UG - (2025-2029)" which might indicate the year.
    # However, for this script, we will assume a simpler approach: 
    # 1st Year = 2025-2029 (Batch 2025)
    # 2nd Year = 2024-2028 (Batch 2024)
    # 3rd Year = 2023-2027 (Batch 2023)
    # 4th Year = 2022-2026 (Batch 2022)
    
    # BUT, the provided CSV snippet shows "STUDENT DETAILS UG - (2025-2029)" and "DEPARTMENT OF B.TECH IT".
    # Since I don't have the full CSV content for all years yet, I'll write the script to be flexible.
    
    current_year_students = []
    current_year_label = ""
    
    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or all(not cell.strip() for cell in row):
                continue
            
            line_str = ",".join(row)
            if "STUDENT DETAILS UG" in line_str:
                # Reset counts for new year section
                if current_year_students:
                    students_to_import.extend(process_year_group(current_year_students, current_year_label))
                current_year_students = []
                current_year_label = line_str
                continue
            
            if row[0].isdigit(): # S.NO column
                current_year_students.append(row)
        
        # Process last group
        if current_year_students:
            students_to_import.extend(process_year_group(current_year_students, current_year_label))

    print(f"Total students filtered for import: {len(students_to_import)}")
    
    # Import logic
    success_count = 0
    error_count = 0
    
    for student_data in students_to_import:
        try:
            # Map data
            # S.NO:0, NAME:1, REGISTER NO:2, GENDER:3, DOB:4, MOBILE:5, EMAIL:6, BLOOD:7, AADHAR:8, UMIS:9, COMMUNITY:10...
            name = student_data[1].strip()
            reg_num = student_data[2].strip()
            email = student_data[6].strip()
            
            # Password: Name@123
            clean_name = name.replace(" ", "")
            default_password = f"{clean_name}@123"
            hashed_pwd = await hash_password(default_password)
            
            # Semester and Batch from year
            year_label = student_data[-1] # We'll append year code in process_year_group
            batch, semester = map_year_to_batch_and_semester(year_label)
            
            user_id = str(uuid.uuid4())
            user_doc = {
                "id": user_id,
                "email": email,
                "name": name,
                "password": hashed_pwd,
                "role": "student",
                "department_id": dept_id,
                "permissions": [],
                "sub_roles": [],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Check unique constraints
            existing_user = await db.users.find_one({"email": email})
            if existing_user:
                print(f"Skipping duplicate email: {email}")
                continue
                
            existing_student = await db.students.find_one({"register_number": reg_num})
            if existing_student:
                print(f"Skipping duplicate register number: {reg_num}")
                continue

            await db.users.insert_one(user_doc)
            
            student_id = str(uuid.uuid4())
            student_doc = {
                "id": student_id,
                "user_id": user_id,
                "roll_number": reg_num, # Mapping register number to roll_number too
                "register_number": reg_num,
                "department_id": dept_id,
                "batch": batch,
                "year": int((semester + 1) / 2),
                "semester": semester,
                "section": "A", # Default
                "date_of_birth": student_data[4],
                "gender": student_data[3],
                "blood_group": student_data[7],
                "mobile_number": student_data[5],
                "email": email,
                "community": student_data[10],
                "umis_id": student_data[9],
                "aadhar_number": student_data[8],
                "admission_quota": student_data[11],
                "cgpa": 8.0, # Fixed demo value
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "created_by": admin_user["id"]
            }
            
            await db.students.insert_one(student_doc)
            success_count += 1
            
        except Exception as e:
            print(f"Error importing student {student_data[1]}: {str(e)}")
            error_count += 1

    print(f"Import complete: {success_count} succeeded, {error_count} failed.")

def process_year_group(rows, label):
    # Year logic
    # 1st Year (2025-2029) -> First 10
    # 2nd Year (2024-2028) -> First 10
    # 3rd Year (2023-2027) -> First 10
    # 4th Year (2022-2026) -> ALL
    
    year_code = ""
    if "2025" in label: year_code = "1"
    elif "2024" in label: year_code = "2"
    elif "2023" in label: year_code = "3"
    elif "2022" in label: year_code = "4"
    
    if not year_code: return []
    
    processed = []
    limit = 10 if year_code != "4" else len(rows)
    
    for i, row in enumerate(rows):
        if i >= limit: break
        # Add year code for mapping later
        row_copy = list(row)
        row_copy.append(year_code)
        processed.append(row_copy)
        
    return processed

def map_year_to_batch_and_semester(year_code):
    mapping = {
        "1": ("2025-2029", 1),
        "2": ("2024-2028", 3),
        "3": ("2023-2027", 5),
        "4": ("2022-2026", 7)
    }
    return mapping.get(year_code, ("2025-2029", 1))

if __name__ == "__main__":
    asyncio.run(import_students())
