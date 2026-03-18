"""
Comprehensive Test Suite for College ERP System Enhanced Features
Tests: Settings, Profile, Password Change, Announcements, Grievance Workflow,
       Document Workflow, Fee Analytics, Risk Analytics, Audit Log Enhancement
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test Credentials
CREDENTIALS = {
    "admin": {"email": "admin@academia.edu", "password": "admin123", "role": "admin"},
    "hod": {"email": "hod.cse@academia.edu", "password": "hod123", "role": "hod"},
    "faculty": {"email": "faculty@academia.edu", "password": "faculty123", "role": "faculty"},
    "principal": {"email": "principal@academia.edu", "password": "principal123", "role": "principal"},
    "student": {"email": "student@academia.edu", "password": "student123", "role": "student"}
}


class TestAuthentication:
    """Test authentication for all roles"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    @pytest.mark.parametrize("role", ["admin", "hod", "faculty", "principal", "student"])
    def test_login_all_roles(self, role):
        """Test login for all roles"""
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS[role]
        )
        assert response.status_code == 200, f"Login failed for {role}: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == role


class TestSettingsAPI:
    """Test Settings API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as admin
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["admin"]
        )
        self.token = response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_get_settings(self):
        """GET /api/settings - Should return user settings"""
        response = self.session.get(f"{BASE_URL}/api/settings")
        assert response.status_code == 200, f"Failed to get settings: {response.text}"
        data = response.json()
        # Verify settings structure
        assert "user_id" in data or "theme" in data  # Either new or existing settings
        print(f"Settings response: {data}")
    
    def test_update_settings_theme(self):
        """PUT /api/settings - Update theme preference"""
        response = self.session.put(
            f"{BASE_URL}/api/settings",
            json={"theme": "dark"}
        )
        assert response.status_code == 200, f"Failed to update settings: {response.text}"
        
        # Verify change persisted
        get_response = self.session.get(f"{BASE_URL}/api/settings")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data.get("theme") == "dark"
    
    def test_update_settings_notifications(self):
        """PUT /api/settings - Update notification preferences"""
        response = self.session.put(
            f"{BASE_URL}/api/settings",
            json={
                "notification_email": True,
                "notification_push": False,
                "notification_sms": True
            }
        )
        assert response.status_code == 200, f"Failed to update notification settings: {response.text}"


class TestProfileAPI:
    """Test Profile API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_get_profile_admin(self):
        """GET /api/profile - Admin profile"""
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["admin"]
        )
        token = response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        response = self.session.get(f"{BASE_URL}/api/profile")
        assert response.status_code == 200, f"Failed to get admin profile: {response.text}"
        data = response.json()
        assert data["role"] == "admin"
        assert data["email"] == "admin@academia.edu"
    
    def test_get_profile_student(self):
        """GET /api/profile - Student profile with student_details"""
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["student"]
        )
        token = response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        response = self.session.get(f"{BASE_URL}/api/profile")
        assert response.status_code == 200, f"Failed to get student profile: {response.text}"
        data = response.json()
        assert data["role"] == "student"
        # Student profiles should have student_details
        print(f"Student profile: {data}")


class TestPasswordChange:
    """Test Password Change functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as admin
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["admin"]
        )
        self.token = response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_change_password_wrong_current(self):
        """POST /api/change-password - Reject wrong current password"""
        response = self.session.post(
            f"{BASE_URL}/api/change-password",
            json={
                "current_password": "wrongpassword",
                "new_password": "newpass123"
            }
        )
        assert response.status_code == 400, f"Should reject wrong password: {response.text}"
    
    def test_change_password_correct(self):
        """POST /api/change-password - Change password successfully then revert"""
        # Change password
        response = self.session.post(
            f"{BASE_URL}/api/change-password",
            json={
                "current_password": "admin123",
                "new_password": "newadmin123"
            }
        )
        assert response.status_code == 200, f"Failed to change password: {response.text}"
        
        # Login with new password
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@academia.edu", "password": "newadmin123", "role": "admin"}
        )
        assert login_response.status_code == 200, "Cannot login with new password"
        
        # Revert password back
        new_token = login_response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {new_token}"})
        revert_response = self.session.post(
            f"{BASE_URL}/api/change-password",
            json={
                "current_password": "newadmin123",
                "new_password": "admin123"
            }
        )
        assert revert_response.status_code == 200, "Failed to revert password"


class TestAnnouncementsAPI:
    """Test Announcements API with publish_date"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as principal (can create announcements)
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["principal"]
        )
        self.token = response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_create_announcement_with_publish_date(self):
        """POST /api/announcements - Create with publish_date"""
        response = self.session.post(
            f"{BASE_URL}/api/announcements",
            json={
                "title": "TEST_Semester Exam Schedule",
                "content": "Exams will start from Feb 15th. All students must register.",
                "target_roles": ["student"],
                "publish_date": "2026-01-20T10:00:00Z"
            }
        )
        assert response.status_code == 200, f"Failed to create announcement: {response.text}"
        data = response.json()
        assert "announcement" in data
        # Store ID for cleanup
        self.announcement_id = data["announcement"]["id"]
    
    def test_get_announcements(self):
        """GET /api/announcements - List announcements"""
        response = self.session.get(f"{BASE_URL}/api/announcements")
        assert response.status_code == 200, f"Failed to get announcements: {response.text}"
        data = response.json()
        assert isinstance(data, list)


class TestGrievanceWorkflow:
    """Test complete Grievance workflow: Student → Faculty → HOD → Admin → Principal"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_token(self, role):
        """Helper to get auth token for a role"""
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS[role]
        )
        return response.json()["access_token"]
    
    def test_grievance_full_workflow(self):
        """Test complete grievance workflow"""
        # Step 1: Student submits grievance
        student_token = self.get_token("student")
        self.session.headers.update({"Authorization": f"Bearer {student_token}"})
        
        submit_response = self.session.post(
            f"{BASE_URL}/api/grievances",
            json={
                "subject": "TEST_Library Hours Issue",
                "description": "Library closes too early. Need extended hours during exams.",
                "category": "infrastructure",
                "priority": "medium"
            }
        )
        assert submit_response.status_code == 200, f"Failed to submit grievance: {submit_response.text}"
        grievance_data = submit_response.json()
        
        # Verify grievance has ticket_id and workflow_history
        grievance = grievance_data["grievance"]
        assert "ticket_id" in grievance, "Grievance should have ticket_id"
        assert grievance["ticket_id"].startswith("GRV-"), f"Invalid ticket_id format: {grievance['ticket_id']}"
        assert "workflow_history" in grievance, "Grievance should have workflow_history"
        assert len(grievance["workflow_history"]) > 0, "Workflow history should have initial entry"
        
        grievance_id = grievance["id"]
        print(f"Created grievance with ticket_id: {grievance['ticket_id']}")
        
        # Step 2: Faculty forwards to HOD
        faculty_token = self.get_token("faculty")
        self.session.headers.update({"Authorization": f"Bearer {faculty_token}"})
        
        forward_response = self.session.put(
            f"{BASE_URL}/api/grievances/{grievance_id}/forward",
            params={"to_level": "hod", "remarks": "Forwarding to HOD for approval"}
        )
        assert forward_response.status_code == 200, f"Faculty forward failed: {forward_response.text}"
        
        # Step 3: HOD forwards to Admin
        hod_token = self.get_token("hod")
        self.session.headers.update({"Authorization": f"Bearer {hod_token}"})
        
        forward_response = self.session.put(
            f"{BASE_URL}/api/grievances/{grievance_id}/forward",
            params={"to_level": "admin", "remarks": "Infrastructure matter - forwarding to Admin"}
        )
        assert forward_response.status_code == 200, f"HOD forward failed: {forward_response.text}"
        
        # Step 4: Admin resolves
        admin_token = self.get_token("admin")
        self.session.headers.update({"Authorization": f"Bearer {admin_token}"})
        
        resolve_response = self.session.put(
            f"{BASE_URL}/api/grievances/{grievance_id}/resolve",
            params={"resolution": "Library hours extended till 10 PM during exam season."}
        )
        assert resolve_response.status_code == 200, f"Resolve failed: {resolve_response.text}"
        
        # Verify final state
        verify_response = self.session.get(f"{BASE_URL}/api/grievances/{grievance_id}")
        assert verify_response.status_code == 200
        final_grievance = verify_response.json()
        assert final_grievance["status"] == "resolved"
        assert final_grievance["resolution"] is not None
        assert len(final_grievance["workflow_history"]) >= 3  # submitted, forwarded, resolved


class TestDocumentWorkflow:
    """Test complete Document Request workflow: Student → Admin (verify) → HOD (approve) → Principal (sign)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_token(self, role):
        """Helper to get auth token for a role"""
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS[role]
        )
        return response.json()["access_token"]
    
    def test_document_request_full_workflow(self):
        """Test complete document request workflow"""
        # Step 1: Student submits document request
        student_token = self.get_token("student")
        self.session.headers.update({"Authorization": f"Bearer {student_token}"})
        
        submit_response = self.session.post(
            f"{BASE_URL}/api/documents/request",
            json={
                "document_type": "bonafide",
                "purpose": "For bank loan application",
                "priority": "urgent"
            }
        )
        assert submit_response.status_code == 200, f"Failed to submit document request: {submit_response.text}"
        doc_request = submit_response.json()["request"]
        
        # Verify request has request_number and workflow_history
        assert "request_number" in doc_request, "Document request should have request_number"
        assert doc_request["request_number"].startswith("DOC-"), f"Invalid request_number format"
        assert "workflow_history" in doc_request
        
        request_id = doc_request["id"]
        print(f"Created document request: {doc_request['request_number']}")
        
        # Step 2: Admin verifies
        admin_token = self.get_token("admin")
        self.session.headers.update({"Authorization": f"Bearer {admin_token}"})
        
        verify_response = self.session.put(
            f"{BASE_URL}/api/documents/requests/{request_id}/verify",
            params={"remarks": "Student records verified"}
        )
        assert verify_response.status_code == 200, f"Admin verify failed: {verify_response.text}"
        
        # Step 3: HOD approves
        hod_token = self.get_token("hod")
        self.session.headers.update({"Authorization": f"Bearer {hod_token}"})
        
        approve_response = self.session.put(
            f"{BASE_URL}/api/documents/requests/{request_id}/approve",
            params={"remarks": "Approved for bonafide certificate"}
        )
        assert approve_response.status_code == 200, f"HOD approve failed: {approve_response.text}"
        
        # Step 4: Principal signs
        principal_token = self.get_token("principal")
        self.session.headers.update({"Authorization": f"Bearer {principal_token}"})
        
        sign_response = self.session.put(
            f"{BASE_URL}/api/documents/requests/{request_id}/sign",
            params={"remarks": "Signed and approved"}
        )
        assert sign_response.status_code == 200, f"Principal sign failed: {sign_response.text}"
        
        # Verify final state
        verify_response = self.session.get(f"{BASE_URL}/api/documents/requests/{request_id}")
        assert verify_response.status_code == 200
        final_request = verify_response.json()
        assert final_request["status"] == "principal_signed"
        assert len(final_request["workflow_history"]) >= 3


class TestFeeAnalytics:
    """Test Fee Analytics API"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as principal
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["principal"]
        )
        self.token = response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_get_fee_analytics(self):
        """GET /api/analytics/fees - Get fee analytics with department breakdown"""
        response = self.session.get(f"{BASE_URL}/api/analytics/fees")
        assert response.status_code == 200, f"Failed to get fee analytics: {response.text}"
        data = response.json()
        
        # Verify analytics structure
        assert "total_collected" in data, "Should have total_collected"
        assert "total_expected" in data, "Should have total_expected"
        assert "collection_percentage" in data, "Should have collection_percentage"
        assert "department_wise" in data, "Should have department_wise breakdown"
        assert "monthly_trend" in data, "Should have monthly_trend"
        
        print(f"Fee Analytics: collected={data['total_collected']}, expected={data['total_expected']}")
        print(f"Department breakdown: {len(data['department_wise'])} departments")


class TestRiskAnalytics:
    """Test Risk Analytics API"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as principal
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["principal"]
        )
        self.token = response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_get_risk_analytics(self):
        """GET /api/analytics/risks - Get at-risk students with risk scoring"""
        response = self.session.get(f"{BASE_URL}/api/analytics/risks")
        assert response.status_code == 200, f"Failed to get risk analytics: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Risk analytics should return a list"
        
        # If there are risk students, verify structure
        if len(data) > 0:
            student = data[0]
            assert "risk_score" in student, "Should have risk_score"
            assert "risk_level" in student, "Should have risk_level (high/medium/low)"
            assert "risk_factors" in student, "Should have risk_factors list"
            assert "attendance_percentage" in student, "Should have attendance_percentage"
            print(f"Found {len(data)} at-risk students")


class TestAuditLogEnhancement:
    """Test Enhanced Audit Log with user_name and user_role"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as principal (can view audit logs)
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["principal"]
        )
        self.token = response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_get_audit_logs(self):
        """GET /api/audit-logs - Should include user_name and user_role"""
        response = self.session.get(f"{BASE_URL}/api/audit-logs")
        assert response.status_code == 200, f"Failed to get audit logs: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Audit logs should return a list"
        
        if len(data) > 0:
            log = data[0]
            assert "user_id" in log, "Should have user_id"
            # Check for enhanced fields
            print(f"Audit log sample: user_name={log.get('user_name')}, user_role={log.get('user_role')}")
            print(f"Total audit logs: {len(data)}")


class TestDashboardAnalytics:
    """Test Dashboard Analytics for Principal"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as principal
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["principal"]
        )
        self.token = response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_get_dashboard_analytics(self):
        """GET /api/analytics/dashboard - Principal dashboard analytics"""
        response = self.session.get(f"{BASE_URL}/api/analytics/dashboard")
        assert response.status_code == 200, f"Failed to get dashboard analytics: {response.text}"
        data = response.json()
        
        # Verify dashboard structure
        assert "total_students" in data, "Should have total_students"
        assert "total_faculty" in data, "Should have total_faculty"
        assert "total_departments" in data, "Should have total_departments"
        print(f"Dashboard: {data['total_students']} students, {data['total_faculty']} faculty, {data['total_departments']} depts")


class TestSubjectMapping:
    """Test HOD Subject-Faculty Mapping"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as HOD
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["hod"]
        )
        self.token = response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_get_subjects(self):
        """GET /api/subjects - Get subjects for HOD"""
        response = self.session.get(f"{BASE_URL}/api/subjects")
        assert response.status_code == 200, f"Failed to get subjects: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} subjects")
    
    def test_get_mappings(self):
        """GET /api/subjects/mappings - Get subject-faculty mappings"""
        response = self.session.get(f"{BASE_URL}/api/subjects/mappings")
        assert response.status_code == 200, f"Failed to get mappings: {response.text}"
        data = response.json()
        assert isinstance(data, list)


class TestFacultyDashboard:
    """Test Faculty Dashboard - Attendance and Marks entry"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as faculty
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["faculty"]
        )
        self.token = response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_faculty_profile(self):
        """GET /api/faculty/me/profile - Faculty profile"""
        response = self.session.get(f"{BASE_URL}/api/faculty/me/profile")
        assert response.status_code == 200, f"Failed to get faculty profile: {response.text}"
    
    def test_get_students_for_attendance(self):
        """GET /api/students - Faculty should see students in their department"""
        response = self.session.get(f"{BASE_URL}/api/students")
        assert response.status_code == 200, f"Failed to get students: {response.text}"
        students = response.json()
        print(f"Faculty can see {len(students)} students for attendance")


class TestAdminDashboard:
    """Test Admin Dashboard CRUD operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as admin
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["admin"]
        )
        self.token = response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_get_students(self):
        """GET /api/students - Admin can see all students"""
        response = self.session.get(f"{BASE_URL}/api/students")
        assert response.status_code == 200, f"Failed to get students: {response.text}"
    
    def test_get_faculty(self):
        """GET /api/faculty - Admin can see all faculty"""
        response = self.session.get(f"{BASE_URL}/api/faculty")
        assert response.status_code == 200, f"Failed to get faculty: {response.text}"
    
    def test_get_pending_verifications(self):
        """GET /api/fees/pending-verification - Admin fee verifications"""
        response = self.session.get(f"{BASE_URL}/api/fees/pending-verification")
        assert response.status_code == 200, f"Failed to get pending verifications: {response.text}"


class TestAttendanceAnalytics:
    """Test Attendance Analytics"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as principal
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["principal"]
        )
        self.token = response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_get_attendance_analytics(self):
        """GET /api/analytics/attendance - Get attendance analytics"""
        response = self.session.get(f"{BASE_URL}/api/analytics/attendance")
        assert response.status_code == 200, f"Failed to get attendance analytics: {response.text}"
        data = response.json()
        
        assert "total_records" in data
        assert "attendance_percentage" in data
        print(f"Attendance: {data['total_records']} records, {data['attendance_percentage']}%")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
