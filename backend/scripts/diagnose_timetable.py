from pymongo import MongoClient

def diagnose_data():
    client = MongoClient("mongodb://localhost:27017")
    db = client["academia_erp"]
    
    # 1. Check a student
    student = db.students.find_one({"roll_number": "22CS01"}) # Assuming some roll no, or just find any
    if not student: student = db.students.find_one({})
    
    if student:
        print(f"Student: {student.get('roll_number')}, DeptID: {student.get('department_id')}")
        dept_id = student.get('department_id')
        
        # 2. Check if subjects exist for this dept
        subjects = list(db.subjects.find({"department_id": dept_id}))
        print(f"Subjects for this Dept ({dept_id}): {len(subjects)}")
        for s in subjects:
            print(f"  - {s['code']}: {s['name']}")
            
        # 3. Check if mappings exist for these subjects
        if subjects:
            sub_ids = [s['id'] for s in subjects]
            mappings = list(db.subject_faculty_mappings.find({"subject_id": {"$in": sub_ids}}))
            print(f"Mappings for these subjects: {len(mappings)}")
            for m in mappings:
                print(f"    Mapping: {m.get('subject_id')} -> {m.get('section')}, Sem: {m.get('semester')}, Day: {m.get('day')}")

if __name__ == "__main__":
    diagnose_data()
