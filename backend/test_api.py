import requests
import json
import urllib3
urllib3.disable_warnings()

BASE_URL = "http://localhost:8000/api"

# 1. Login
resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@academia.edu", "password": "admin", "role": "admin"}, verify=False)
if resp.status_code != 200:
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@academia.edu", "password": "password", "role": "admin"}, verify=False)
if resp.status_code != 200:
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@academia.edu", "password": "admin123", "role": "admin"}, verify=False)

if resp.status_code == 200:
    token = resp.json().get("access_token")
    print("Logged in successfully.")
else:
    print(f"Login failed: {resp.text}")
    exit(1)

# 2. Create Student
headers = {
    "Authorization": f"Bearer {token}"
}

data = {
    "name": "Test Python",
    "email": "testpy@academia.edu",
    "password": "password123",
    "roll_number": "512722205049",
    "department_id": "dept_cse",
    "batch": "2023-2027",
    "year": 1,
    "semester": 1,
}

resp = requests.post(f"{BASE_URL}/students/enhanced", data=data, headers=headers)
print("Create response:", resp.status_code)
try:
    with open("test_api_out.txt", "w") as f:
        f.write(json.dumps(resp.json(), indent=2))
except:
    with open("test_api_out.txt", "w") as f:
        f.write(resp.text)
