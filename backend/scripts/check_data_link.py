from pymongo import MongoClient

def check_data_link():
    client = MongoClient("mongodb://localhost:27017")
    db = client["academia_erp"]
    
    # 1. List all departments
    depts = list(db.departments.find({}, {"id": 1, "name": 1, "code": 1}))
    print("Departments:")
    for d in depts:
        sub_count = db.subjects.count_documents({"department_id": d["id"]})
        print(f"  {d['code']} ({d['id']}): {d['name']} - Subjects: {sub_count}")
        
    # 2. Check student departments
    students = list(db.students.find({}, {"roll_number": 1, "department_id": 1}).limit(5))
    print("\nSample Students:")
    for s in students:
        dept = db.departments.find_one({"id": s.get("department_id")})
        d_name = dept["name"] if dept else "MISSING DEPT"
        print(f"  Student {s.get('roll_number')} - DeptID: {s.get('department_id')} ({d_name})")

if __name__ == "__main__":
    check_data_link()
