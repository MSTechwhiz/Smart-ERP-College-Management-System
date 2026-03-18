from pymongo import MongoClient
import json

def check_linkage():
    client = MongoClient("mongodb://localhost:27017")
    db = client["academia_erp"]
    
    # Check Agalya
    user = db.users.find_one({"email": "aagalya236@gmail.com"})
    if not user:
        print("User not found")
        return
        
    print(f"User: {user['email']}, ID: {user['id']}")
    
    student = db.students.find_one({"user_id": user["id"]})
    if student:
        print(f"Student Profile found! ID: {student['id']}, Dept: {student.get('department_id')}")
    else:
        print("Student Profile NOT found by user_id!")
        # Search by name?
        student_by_name = db.students.find_one({"name": user["name"]})
        if student_by_name:
             print(f"Found student by name instead! profile user_id={student_by_name.get('user_id')}")

if __name__ == "__main__":
    check_linkage()
