import pytest

@pytest.mark.asyncio
async def test_attendance_workflow(client, admin_token, mock_db):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Create required entities
    await mock_db.subjects.insert_one({"id": "SUB01", "name": "Python", "code": "CS101"})
    
    import uuid
    attendance_data = {
        "student_id": f"STU-{uuid.uuid4().hex[:4]}",
        "subject_id": "SUB01",
        "date": "2024-03-20",
        "status": "present"
    }
    response = await client.post("/api/attendance", json=attendance_data, headers=headers)
    assert response.status_code == 200
    assert "Attendance marked" in response.json()["message"]

@pytest.mark.asyncio
async def test_marks_workflow(client, admin_token, mock_db):
    headers = {"Authorization": f"Bearer {admin_token}"}
    marks_data = {
        "student_id": f"STU-{uuid.uuid4().hex[:4]}",
        "subject_id": "SUB01",
        "marks": 85,
        "exam_type": "cia1",
        "academic_year": "2024-25",
        "semester": 1
    }
    response = await client.post("/api/marks", json=marks_data, headers=headers)
    assert response.status_code == 200
    assert "Marks entered" in response.json()["message"]

@pytest.mark.asyncio
async def test_fee_payments_list(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get("/api/fees/payments?skip=0&limit=10", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
