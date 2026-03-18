import pytest
import uuid
from datetime import datetime, timezone
from app.services.auth_service import AuthService
from app.services.student_service import StudentService
from app.services.document_service import DocumentService
from app.schemas.auth_schema import UserCreate
from app.schemas.student_schema import StudentCreate
from app.schemas.document_schema import DocumentRequestCreate

@pytest.mark.asyncio
async def test_auth_service_register(db):
    auth_service = AuthService()
    user_data = UserCreate(
        email="test@example.com",
        password="testpassword",
        name="Test User",
        role="student"
    )
    user = await auth_service.register_user(user_data)
    assert user["email"] == "test@example.com"
    assert user["name"] == "Test User"
    assert user["role"] == "student"
    assert "password" not in user

@pytest.mark.asyncio
async def test_student_service_create(db):
    auth_service = AuthService()
    student_service = StudentService()
    
    # Register user first
    user_data = UserCreate(
        email="student@example.com",
        password="studentpassword",
        name="Student User",
        role="student"
    )
    user = await auth_service.register_user(user_data)
    
    # Create student profile
    student_data = StudentCreate(
        user_id=user["id"],
        roll_number="ST001",
        department_id="DEPT001",
        batch="2023-2027"
    )
    student = await student_service.create_student(student_data)
    assert student["roll_number"] == "ST001"
    assert student["user_id"] == user["id"]

@pytest.mark.asyncio
async def test_document_service_request(db):
    auth_service = AuthService()
    student_service = StudentService()
    doc_service = DocumentService()
    
    # Setup student
    user_data = UserCreate(
        email="doc_student@example.com",
        password="password",
        name="Doc Student",
        role="student"
    )
    user = await auth_service.register_user(user_data)
    
    # Create student profile
    student_data = StudentCreate(
        user_id=user["id"],
        roll_number="DOC001",
        department_id="DEPT001",
        batch="2023-2027"
    )
    await student_service.create_student(student_data)
    
    # Create document request
    request_data = DocumentRequestCreate(
        document_type="bonafide",
        remarks="For internship"
    )
    doc_request = await doc_service.create_document_request(request_data, user)
    assert doc_request["document_type"] == "bonafide"
    assert doc_request["status"] == "submitted"
    assert len(doc_request["workflow_history"]) == 1
    assert doc_request["workflow_history"][0]["action"] == "submitted"

@pytest.mark.asyncio
async def test_document_service_workflow(db):
    # Setup student and request
    auth_service = AuthService()
    student_service = StudentService()
    doc_service = DocumentService()
    
    user_data = UserCreate(
        email="workflow_student@example.com",
        password="password",
        name="Workflow Student",
        role="student"
    )
    user = await auth_service.register_user(user_data)
    
    student_data = StudentCreate(
        user_id=user["id"],
        roll_number="WF001",
        department_id="DEPT001",
        batch="2023-2027"
    )
    await student_service.create_student(student_data)
    
    request_data = DocumentRequestCreate(
        document_type="transcript",
        remarks="For higher studies"
    )
    doc_request = await doc_service.create_document_request(request_data, user)
    request_id = doc_request["id"]
    
    # Office Verification (Admin)
    admin_user = {"id": "admin_id", "name": "Admin", "role": "admin"}
    response = await doc_service.update_workflow_status(
        request_id, admin_user, "verified", "office_verified", 
        next_level="hod", required_level="office"
    )
    assert response["status"] == "office_verified"
    
    # HOD Approval
    hod_user = {"id": "hod_id", "name": "HOD", "role": "hod"}
    response = await doc_service.update_workflow_status(
        request_id, hod_user, "approved", "hod_approved", 
        next_level="principal", required_level="hod"
    )
    assert response["status"] == "hod_approved"
    
    # Principal Sign
    principal_user = {"id": "principal_id", "name": "Principal", "role": "principal"}
    response = await doc_service.update_workflow_status(
        request_id, principal_user, "signed", "principal_signed", 
        next_level="generated", required_level="principal"
    )
    assert response["status"] == "principal_signed"
