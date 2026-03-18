import pytest

@pytest.mark.asyncio
async def test_create_faculty(client, admin_token, mock_db):
    headers = {"Authorization": f"Bearer {admin_token}"}
    import uuid
    faculty_data = {
        "email": f"faculty_{uuid.uuid4().hex[:8]}@test.com",
        "name": "Test Faculty",
        "password": "Password123",
        "employee_id": f"EMP{uuid.uuid4().hex[:4].upper()}",
        "department_id": "DEPT01",
        "designation": "Assistant Professor",
        "specialization": "Computer Science"
    }
    response = await client.post("/api/faculty", json=faculty_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Faculty created"
    
    # Verify in DB
    faculty = await mock_db.faculty.find_one({"employee_id": faculty_data["employee_id"]})
    assert faculty is not None
    user = await mock_db.users.find_one({"id": faculty["user_id"]})
    assert user["email"] == faculty_data["email"]
