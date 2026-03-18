import pytest
import uuid

@pytest.mark.asyncio
async def test_create_student(client, admin_token, mock_db):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    student_data = {
        "email": f"student_{uuid.uuid4().hex[:8]}@test.com",
        "name": "Test Student",
        "password": "password123",
        "roll_number": f"ROLL{uuid.uuid4().hex[:4].upper()}",
        "department_id": "dept-123",
        "batch": "2024-2028",
        "semester": 1,
        "regulation": "R2023"
    }
    
    response = await client.post("/api/students", json=student_data, headers=headers)
    if response.status_code != 200:
        print(f"FAILED: {response.status_code} {response.json()}")
    assert response.status_code == 200
    assert response.json()["message"] == "Student created"
    
    # Verify in DB
    student = await mock_db.students.find_one({"roll_number": student_data["roll_number"]})
    assert student is not None
    user = await mock_db.users.find_one({"id": student["user_id"]})
    assert user["email"] == student_data["email"]

@pytest.mark.asyncio
async def test_get_students_paginated(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get("/api/students?skip=0&limit=10", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_student_not_found(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get("/api/students/nonexistent", headers=headers)
    assert response.status_code == 404
