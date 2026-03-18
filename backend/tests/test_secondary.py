import pytest

@pytest.mark.asyncio
async def test_announcement_workflow(client, admin_token, mock_db):
    headers = {"Authorization": f"Bearer {admin_token}"}
    import uuid
    ann_data = {
        "title": f"Exam Schedule {uuid.uuid4().hex[:4]}",
        "content": "Final exams start on Monday.",
        "target_roles": ["student"],
        "is_active": True
    }
    response = await client.post("/api/announcements", json=ann_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Announcement created"

@pytest.mark.asyncio
async def test_grievance_workflow(client, admin_token, mock_db):
    headers = {"Authorization": f"Bearer {admin_token}"}
    grievance_data = {
        "title": "Hostel Issue",
        "description": "No water in Block A.",
        "type": "Hostel",
        "priority": "high"
    }
    # Need a student user for grievance
    student_user = {
        "id": "student-123",
        "email": "stu@test.com",
        "name": "Test Student",
        "role": "student",
        "is_active": True,
        "permissions": [],
        "sub_roles": []
    }
    await mock_db.users.insert_one(student_user)
    from app.core.security import create_token
    stu_token = create_token(student_user)
    stu_headers = {"Authorization": f"Bearer {stu_token}"}
    
    response = await client.post("/api/grievances", json=grievance_data, headers=stu_headers)
    assert response.status_code == 200
    assert "Grievance submitted" in response.json()["message"]

@pytest.mark.asyncio
async def test_attendance_workflow(client, admin_token, mock_db):
    headers = {"Authorization": f"Bearer {admin_token}"}
    attendance_data = {
        "student_id": "student-123",
        "course_id": "course-456",
        "date": "2023-10-26",
        "status": "present"
    }
    # Need a student user for attendance, or an instructor to mark it.
    # For this test, let's assume an admin or instructor marks attendance.
    # If student marks their own, stu_headers would be used.
    
    response = await client.post("/api/attendance", json=attendance_data, headers=headers)
    assert response.status_code == 200
    # The actual message might be "Attendance marked successfully" or similar
    assert "Attendance marked" in response.json()["message"]
