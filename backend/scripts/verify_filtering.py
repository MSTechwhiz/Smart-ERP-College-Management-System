import requests
import json

BASE_URL = "http://localhost:8002/api"

def login():
    print("Logging in as admin...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@academia.edu",
        "password": "admin123",
        "role": "admin"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def test_filtering(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Get all students (no limit)
    print("\n1. Testing 'getAll' (no limit)...")
    res = requests.get(f"{BASE_URL}/students", headers=headers, params={"limit": None})
    data = res.json()
    total_count = data.get("total", 0)
    student_count = len(data.get("students", []))
    print(f"Total: {total_count}, Students returned: {student_count}")
    
    # 2. Test Category filter (PMSS)
    print("\n2. Testing 'PMSS' category filter...")
    res = requests.get(f"{BASE_URL}/students", headers=headers, params={"category": "PMSS", "limit": None})
    data = res.json()
    print(f"Total PMSS: {data.get('total')}, Students returned: {len(data.get('students', []))}")
    
    # 3. Test Year filter (4)
    print("\n3. Testing 'Year 4' filter...")
    res = requests.get(f"{BASE_URL}/students", headers=headers, params={"year": 4, "limit": None})
    data = res.json()
    print(f"Total Year 4: {data.get('total')}, Students returned: {len(data.get('students', []))}")
    
    # 4. Test Search filter
    print("\n4. Testing search filter (search for 'Sanjay')...")
    res = requests.get(f"{BASE_URL}/students", headers=headers, params={"search": "Sanjay"})
    data = res.json()
    print(f"Search results for 'Sanjay': {data.get('total')}")
    for s in data.get("students", []):
        print(f"- {s['name']} ({s['roll_number']})")

if __name__ == "__main__":
    token = login()
    if token:
        test_filtering(token)
