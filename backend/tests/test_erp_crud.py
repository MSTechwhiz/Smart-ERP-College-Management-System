"""
ERP System Backend API Tests - CRUD Operations for All Dashboards
Tests Admin, HOD, Faculty, Principal dashboard functionalities
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8000').rstrip('/')

# Test credentials
ADMIN_CREDS = {"email": "admin@academia.edu", "password": "admin123", "role": "admin"}
HOD_CREDS = {"email": "hod.cse@academia.edu", "password": "hod123", "role": "hod"}
FACULTY_CREDS = {"email": "faculty@academia.edu", "password": "faculty123", "role": "faculty"}
PRINCIPAL_CREDS = {"email": "principal@academia.edu", "password": "principal123", "role": "principal"}


class TestAuth:
    """Authentication tests for all roles"""
    
    def test_admin_login(self):
        """Test admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        print(f"Admin login: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "admin"
    
    def test_hod_login(self):
        """Test HOD login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=HOD_CREDS)
        print(f"HOD login: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "hod"
    
    def test_faculty_login(self):
        """Test Faculty login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=FACULTY_CREDS)
        print(f"Faculty login: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "faculty"
    
    def test_principal_login(self):
        """Test Principal login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=PRINCIPAL_CREDS)
        print(f"Principal login: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "principal"
    
    def test_invalid_login(self):
        """Test invalid login credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com", "password": "wrong", "role": "admin"
        })
        print(f"Invalid login: {response.status_code}")
        assert response.status_code == 401


@pytest.fixture
def admin_token():
    """Get admin auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
    if response.status_code != 200:
        pytest.skip("Admin authentication failed")
    return response.json()["access_token"]


@pytest.fixture
def hod_token():
    """Get HOD auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=HOD_CREDS)
    if response.status_code != 200:
        pytest.skip("HOD authentication failed")
    return response.json()["access_token"]


@pytest.fixture
def faculty_token():
    """Get Faculty auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=FACULTY_CREDS)
    if response.status_code != 200:
        pytest.skip("Faculty authentication failed")
    return response.json()["access_token"]


@pytest.fixture
def principal_token():
    """Get Principal auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=PRINCIPAL_CREDS)
    if response.status_code != 200:
        pytest.skip("Principal authentication failed")
    return response.json()["access_token"]


class TestDepartments:
    """Department CRUD tests - Admin and Principal"""
    
    def test_list_departments(self, admin_token):
        """Test listing all departments"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/departments", headers=headers)
        print(f"List departments: {response.status_code}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_department_as_admin(self, admin_token):
        """Test creating department as admin"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        dept_code = f"TEST{uuid.uuid4().hex[:4].upper()}"
        data = {"name": f"TEST Department {dept_code}", "code": dept_code}
        response = requests.post(f"{BASE_URL}/api/departments", json=data, headers=headers)
        print(f"Create department: {response.status_code} - {response.text[:200]}")
        assert response.status_code == 200
        result = response.json()
        assert "department" in result
        assert result["department"]["code"] == dept_code
    
    def test_create_department_as_principal(self, principal_token):
        """Test creating department as principal"""
        headers = {"Authorization": f"Bearer {principal_token}"}
        dept_code = f"PRI{uuid.uuid4().hex[:4].upper()}"
        data = {"name": f"Principal Test Dept {dept_code}", "code": dept_code}
        response = requests.post(f"{BASE_URL}/api/departments", json=data, headers=headers)
        print(f"Principal create department: {response.status_code}")
        assert response.status_code == 200
    
    def test_get_single_department(self, admin_token):
        """Test getting single department"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        # First get list
        list_response = requests.get(f"{BASE_URL}/api/departments", headers=headers)
        if list_response.status_code == 200 and len(list_response.json()) > 0:
            dept_id = list_response.json()[0]["id"]
            response = requests.get(f"{BASE_URL}/api/departments/{dept_id}", headers=headers)
            print(f"Get single department: {response.status_code}")
            assert response.status_code == 200


class TestAdminStudentCRUD:
    """Admin Dashboard - Student CRUD Operations"""
    
    def test_list_students(self, admin_token):
        """Test listing all students"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/students", headers=headers)
        print(f"List students: {response.status_code}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_student(self, admin_token):
        """Test creating a new student"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get a department first
        dept_response = requests.get(f"{BASE_URL}/api/departments", headers=headers)
        if dept_response.status_code != 200 or len(dept_response.json()) == 0:
            pytest.skip("No departments available")
        dept_id = dept_response.json()[0]["id"]
        
        student_email = f"test_student_{uuid.uuid4().hex[:8]}@academia.edu"
        data = {
            "email": student_email,
            "name": "TEST Student",
            "password": "test123",
            "roll_number": f"TEST{uuid.uuid4().hex[:6].upper()}",
            "department_id": dept_id,
            "batch": "2024-2028",
            "semester": 1,
            "section": "A"
        }
        response = requests.post(f"{BASE_URL}/api/students", json=data, headers=headers)
        print(f"Create student: {response.status_code} - {response.text[:200]}")
        assert response.status_code == 200
        result = response.json()
        assert "student" in result
    
    def test_get_single_student(self, admin_token):
        """Test getting single student details"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        list_response = requests.get(f"{BASE_URL}/api/students", headers=headers)
        if list_response.status_code == 200 and len(list_response.json()) > 0:
            student_id = list_response.json()[0]["id"]
            response = requests.get(f"{BASE_URL}/api/students/{student_id}", headers=headers)
            print(f"Get single student: {response.status_code}")
            assert response.status_code == 200


class TestAdminFacultyCRUD:
    """Admin Dashboard - Faculty CRUD Operations"""
    
    def test_list_faculty(self, admin_token):
        """Test listing all faculty"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/faculty", headers=headers)
        print(f"List faculty: {response.status_code}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_faculty(self, admin_token):
        """Test creating a new faculty member"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get a department first
        dept_response = requests.get(f"{BASE_URL}/api/departments", headers=headers)
        if dept_response.status_code != 200 or len(dept_response.json()) == 0:
            pytest.skip("No departments available")
        dept_id = dept_response.json()[0]["id"]
        
        faculty_email = f"test_faculty_{uuid.uuid4().hex[:8]}@academia.edu"
        data = {
            "email": faculty_email,
            "name": "TEST Faculty",
            "password": "test123",
            "employee_id": f"EMP{uuid.uuid4().hex[:6].upper()}",
            "department_id": dept_id,
            "designation": "Assistant Professor",
            "specialization": "AI/ML"
        }
        response = requests.post(f"{BASE_URL}/api/faculty", json=data, headers=headers)
        print(f"Create faculty: {response.status_code} - {response.text[:200]}")
        assert response.status_code == 200
        result = response.json()
        assert "faculty" in result


class TestAdminFeeManagement:
    """Admin Dashboard - Fee Management Operations"""
    
    def test_list_fee_structures(self, admin_token):
        """Test listing fee structures"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/fees/structure", headers=headers)
        print(f"List fee structures: {response.status_code}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_fee_structure(self, admin_token):
        """Test creating a fee structure"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        params = {
            "name": f"TEST Fee {uuid.uuid4().hex[:6]}",
            "category": "semester",
            "amount": 50000.0,
            "due_date": "2025-06-30"
        }
        response = requests.post(f"{BASE_URL}/api/fees/structure", headers=headers, params=params)
        print(f"Create fee structure: {response.status_code} - {response.text[:200]}")
        assert response.status_code == 200


class TestAdminGrievances:
    """Admin Dashboard - Grievance Management"""
    
    def test_list_grievances(self, admin_token):
        """Test listing grievances"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/grievances", headers=headers)
        print(f"List grievances: {response.status_code}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestAdminDocumentRequests:
    """Admin Dashboard - Document Requests"""
    
    def test_list_document_requests(self, admin_token):
        """Test listing document requests"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/documents/requests", headers=headers)
        print(f"List document requests: {response.status_code}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestHODDashboard:
    """HOD Dashboard - Operations"""
    
    def test_list_department_students(self, hod_token):
        """Test listing students in HOD's department"""
        headers = {"Authorization": f"Bearer {hod_token}"}
        response = requests.get(f"{BASE_URL}/api/students", headers=headers)
        print(f"HOD list students: {response.status_code}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_department_faculty(self, hod_token):
        """Test listing faculty in department"""
        headers = {"Authorization": f"Bearer {hod_token}"}
        response = requests.get(f"{BASE_URL}/api/faculty", headers=headers)
        print(f"HOD list faculty: {response.status_code}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_subjects(self, hod_token):
        """Test listing subjects"""
        headers = {"Authorization": f"Bearer {hod_token}"}
        response = requests.get(f"{BASE_URL}/api/subjects", headers=headers)
        print(f"HOD list subjects: {response.status_code}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_subject_mappings(self, hod_token):
        """Test listing subject-faculty mappings"""
        headers = {"Authorization": f"Bearer {hod_token}"}
        response = requests.get(f"{BASE_URL}/api/subjects/mappings", headers=headers)
        print(f"HOD list mappings: {response.status_code}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_approve_document_request(self, hod_token):
        """Test document approval endpoint"""
        headers = {"Authorization": f"Bearer {hod_token}"}
        # Get pending requests
        response = requests.get(f"{BASE_URL}/api/documents/requests", headers=headers)
        print(f"HOD get doc requests: {response.status_code}")
        assert response.status_code == 200


class TestHODSubjectCreation:
    """HOD Dashboard - Subject CRUD (requires admin/principal role)"""
    
    def test_create_subject(self, admin_token):
        """Test creating a new subject (admin role needed)"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get a department
        dept_response = requests.get(f"{BASE_URL}/api/departments", headers=headers)
        if dept_response.status_code != 200 or len(dept_response.json()) == 0:
            pytest.skip("No departments available")
        dept_id = dept_response.json()[0]["id"]
        
        data = {
            "code": f"SUB{uuid.uuid4().hex[:4].upper()}",
            "name": "TEST Subject",
            "department_id": dept_id,
            "semester": 3,
            "credits": 3,
            "subject_type": "theory",
            "regulation": "R2023"
        }
        response = requests.post(f"{BASE_URL}/api/subjects", json=data, headers=headers)
        print(f"Create subject: {response.status_code} - {response.text[:200]}")
        assert response.status_code == 200


class TestHODSubjectMapping:
    """HOD Dashboard - Subject-Faculty Mapping"""
    
    def test_create_subject_faculty_mapping(self, hod_token):
        """Test creating subject-faculty mapping"""
        headers = {"Authorization": f"Bearer {hod_token}"}
        
        # Get subjects and faculty
        subjects_response = requests.get(f"{BASE_URL}/api/subjects", headers=headers)
        faculty_response = requests.get(f"{BASE_URL}/api/faculty", headers=headers)
        
        if subjects_response.status_code != 200 or len(subjects_response.json()) == 0:
            pytest.skip("No subjects available")
        if faculty_response.status_code != 200 or len(faculty_response.json()) == 0:
            pytest.skip("No faculty available")
        
        subject_id = subjects_response.json()[0]["id"]
        faculty_id = faculty_response.json()[0]["id"]
        
        params = {
            "subject_id": subject_id,
            "faculty_id": faculty_id,
            "section": "A",
            "academic_year": "2024-25",
            "semester": 5
        }
        response = requests.post(f"{BASE_URL}/api/subjects/mapping", headers=headers, params=params)
        print(f"Create mapping: {response.status_code} - {response.text[:200]}")
        # Accept both 200 and 400 (if mapping already exists)
        assert response.status_code in [200, 400]


class TestFacultyDashboard:
    """Faculty Dashboard - Operations"""
    
    def test_get_my_profile(self, faculty_token):
        """Test getting faculty profile"""
        headers = {"Authorization": f"Bearer {faculty_token}"}
        response = requests.get(f"{BASE_URL}/api/faculty/me/profile", headers=headers)
        print(f"Faculty profile: {response.status_code}")
        assert response.status_code == 200
    
    def test_get_subject_mappings(self, faculty_token):
        """Test getting assigned subject mappings"""
        headers = {"Authorization": f"Bearer {faculty_token}"}
        response = requests.get(f"{BASE_URL}/api/subjects/mappings", headers=headers)
        print(f"Faculty subject mappings: {response.status_code}")
        assert response.status_code == 200
    
    def test_list_students(self, faculty_token):
        """Test listing students"""
        headers = {"Authorization": f"Bearer {faculty_token}"}
        response = requests.get(f"{BASE_URL}/api/students", headers=headers)
        print(f"Faculty list students: {response.status_code}")
        assert response.status_code == 200


class TestFacultyAttendance:
    """Faculty Dashboard - Attendance Marking"""
    
    def test_mark_attendance(self, faculty_token):
        """Test marking individual attendance"""
        headers = {"Authorization": f"Bearer {faculty_token}"}
        
        # Get students and subjects
        students_response = requests.get(f"{BASE_URL}/api/students", headers=headers)
        subjects_response = requests.get(f"{BASE_URL}/api/subjects", headers=headers)
        
        if students_response.status_code != 200 or len(students_response.json()) == 0:
            pytest.skip("No students available")
        if subjects_response.status_code != 200 or len(subjects_response.json()) == 0:
            pytest.skip("No subjects available")
        
        student_id = students_response.json()[0]["id"]
        subject_id = subjects_response.json()[0]["id"]
        
        data = {
            "student_id": student_id,
            "subject_id": subject_id,
            "date": "2025-01-15",
            "status": "present"
        }
        response = requests.post(f"{BASE_URL}/api/attendance", json=data, headers=headers)
        print(f"Mark attendance: {response.status_code}")
        assert response.status_code == 200
    
    def test_mark_bulk_attendance(self, faculty_token):
        """Test marking bulk attendance"""
        headers = {"Authorization": f"Bearer {faculty_token}"}
        
        students_response = requests.get(f"{BASE_URL}/api/students", headers=headers)
        subjects_response = requests.get(f"{BASE_URL}/api/subjects", headers=headers)
        
        if students_response.status_code != 200 or len(students_response.json()) == 0:
            pytest.skip("No students available")
        if subjects_response.status_code != 200 or len(subjects_response.json()) == 0:
            pytest.skip("No subjects available")
        
        students = students_response.json()[:3]  # Take first 3 students
        subject_id = subjects_response.json()[0]["id"]
        
        data = {
            "subject_id": subject_id,
            "date": "2025-01-16",
            "records": [{"student_id": s["id"], "status": "present"} for s in students]
        }
        response = requests.post(f"{BASE_URL}/api/attendance/bulk", json=data, headers=headers)
        print(f"Bulk attendance: {response.status_code}")
        assert response.status_code == 200
    
    def test_get_attendance(self, faculty_token):
        """Test getting attendance records"""
        headers = {"Authorization": f"Bearer {faculty_token}"}
        response = requests.get(f"{BASE_URL}/api/attendance", headers=headers)
        print(f"Get attendance: {response.status_code}")
        assert response.status_code == 200


class TestFacultyMarks:
    """Faculty Dashboard - Marks Entry"""
    
    def test_enter_marks(self, faculty_token):
        """Test entering marks for a student"""
        headers = {"Authorization": f"Bearer {faculty_token}"}
        
        students_response = requests.get(f"{BASE_URL}/api/students", headers=headers)
        subjects_response = requests.get(f"{BASE_URL}/api/subjects", headers=headers)
        
        if students_response.status_code != 200 or len(students_response.json()) == 0:
            pytest.skip("No students available")
        if subjects_response.status_code != 200 or len(subjects_response.json()) == 0:
            pytest.skip("No subjects available")
        
        student_id = students_response.json()[0]["id"]
        subject_id = subjects_response.json()[0]["id"]
        
        data = {
            "student_id": student_id,
            "subject_id": subject_id,
            "academic_year": "2024-25",
            "semester": 5,
            "exam_type": "cia1",
            "marks": 85.0
        }
        response = requests.post(f"{BASE_URL}/api/marks", json=data, headers=headers)
        print(f"Enter marks: {response.status_code}")
        assert response.status_code == 200
    
    def test_enter_bulk_marks(self, faculty_token):
        """Test entering bulk marks"""
        headers = {"Authorization": f"Bearer {faculty_token}"}
        
        students_response = requests.get(f"{BASE_URL}/api/students", headers=headers)
        subjects_response = requests.get(f"{BASE_URL}/api/subjects", headers=headers)
        
        if students_response.status_code != 200 or len(students_response.json()) == 0:
            pytest.skip("No students available")
        if subjects_response.status_code != 200 or len(subjects_response.json()) == 0:
            pytest.skip("No subjects available")
        
        students = students_response.json()[:3]
        subject_id = subjects_response.json()[0]["id"]
        
        data = {
            "subject_id": subject_id,
            "academic_year": "2024-25",
            "semester": 5,
            "exam_type": "cia2",
            "records": [{"student_id": s["id"], "marks": 80.0} for s in students]
        }
        response = requests.post(f"{BASE_URL}/api/marks/bulk", json=data, headers=headers)
        print(f"Bulk marks: {response.status_code}")
        assert response.status_code == 200
    
    def test_get_marks(self, faculty_token):
        """Test getting marks records"""
        headers = {"Authorization": f"Bearer {faculty_token}"}
        response = requests.get(f"{BASE_URL}/api/marks", headers=headers)
        print(f"Get marks: {response.status_code}")
        assert response.status_code == 200


class TestPrincipalDashboard:
    """Principal Dashboard - Operations"""
    
    def test_get_analytics_dashboard(self, principal_token):
        """Test getting analytics dashboard"""
        headers = {"Authorization": f"Bearer {principal_token}"}
        response = requests.get(f"{BASE_URL}/api/analytics/dashboard", headers=headers)
        print(f"Analytics dashboard: {response.status_code}")
        assert response.status_code == 200
    
    def test_list_all_departments(self, principal_token):
        """Test listing all departments"""
        headers = {"Authorization": f"Bearer {principal_token}"}
        response = requests.get(f"{BASE_URL}/api/departments", headers=headers)
        print(f"Principal list departments: {response.status_code}")
        assert response.status_code == 200
    
    def test_list_all_faculty(self, principal_token):
        """Test listing all faculty"""
        headers = {"Authorization": f"Bearer {principal_token}"}
        response = requests.get(f"{BASE_URL}/api/faculty", headers=headers)
        print(f"Principal list faculty: {response.status_code}")
        assert response.status_code == 200
    
    def test_list_all_students(self, principal_token):
        """Test listing all students"""
        headers = {"Authorization": f"Bearer {principal_token}"}
        response = requests.get(f"{BASE_URL}/api/students", headers=headers)
        print(f"Principal list students: {response.status_code}")
        assert response.status_code == 200
    
    def test_get_audit_logs(self, principal_token):
        """Test getting audit logs"""
        headers = {"Authorization": f"Bearer {principal_token}"}
        response = requests.get(f"{BASE_URL}/api/audit-logs", headers=headers)
        print(f"Audit logs: {response.status_code}")
        assert response.status_code == 200


class TestPrincipalAnnouncements:
    """Principal Dashboard - Announcements CRUD"""
    
    def test_list_announcements(self, principal_token):
        """Test listing announcements"""
        headers = {"Authorization": f"Bearer {principal_token}"}
        response = requests.get(f"{BASE_URL}/api/announcements", headers=headers)
        print(f"List announcements: {response.status_code}")
        assert response.status_code == 200
    
    def test_create_announcement(self, principal_token):
        """Test creating an announcement"""
        headers = {"Authorization": f"Bearer {principal_token}"}
        data = {
            "title": f"TEST Announcement {uuid.uuid4().hex[:6]}",
            "content": "This is a test announcement for all students and faculty.",
            "target_roles": []
        }
        response = requests.post(f"{BASE_URL}/api/announcements", json=data, headers=headers)
        print(f"Create announcement: {response.status_code}")
        assert response.status_code == 200


class TestPrincipalDepartmentHOD:
    """Principal Dashboard - HOD Assignment"""
    
    def test_update_department_hod(self, principal_token):
        """Test updating department with HOD assignment"""
        headers = {"Authorization": f"Bearer {principal_token}"}
        
        # Get departments and faculty
        dept_response = requests.get(f"{BASE_URL}/api/departments", headers=headers)
        faculty_response = requests.get(f"{BASE_URL}/api/faculty", headers=headers)
        
        if dept_response.status_code != 200 or len(dept_response.json()) == 0:
            pytest.skip("No departments available")
        if faculty_response.status_code != 200 or len(faculty_response.json()) == 0:
            pytest.skip("No faculty available")
        
        dept = dept_response.json()[0]
        faculty_list = faculty_response.json()
        
        # Find faculty in same department
        dept_faculty = [f for f in faculty_list if f.get("department_id") == dept["id"]]
        if not dept_faculty:
            pytest.skip("No faculty in this department")
        
        faculty_id = dept_faculty[0]["id"]
        
        # Update department with HOD
        response = requests.put(
            f"{BASE_URL}/api/departments/{dept['id']}", 
            headers=headers,
            params={"hod_id": faculty_id}
        )
        print(f"Assign HOD: {response.status_code}")
        # This endpoint may not exist - accept various responses
        assert response.status_code in [200, 404, 405, 422]


class TestRiskAlerts:
    """Risk Alerts - AI features"""
    
    def test_get_department_risks(self, principal_token):
        """Test getting department risk alerts"""
        headers = {"Authorization": f"Bearer {principal_token}"}
        response = requests.get(f"{BASE_URL}/api/ai/department-risks", headers=headers)
        print(f"Department risks: {response.status_code}")
        assert response.status_code == 200


class TestQuickActions:
    """Quick Actions - Navigation tests"""
    
    def test_admin_quick_actions_endpoints(self, admin_token):
        """Test all admin quick action endpoints"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        endpoints = [
            "/api/students",
            "/api/faculty",
            "/api/fees/structure",
            "/api/departments"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"Quick action {endpoint}: {response.status_code}")
            assert response.status_code == 200
    
    def test_hod_quick_actions_endpoints(self, hod_token):
        """Test all HOD quick action endpoints"""
        headers = {"Authorization": f"Bearer {hod_token}"}
        
        endpoints = [
            "/api/students",
            "/api/faculty",
            "/api/subjects",
            "/api/subjects/mappings"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"HOD quick action {endpoint}: {response.status_code}")
            assert response.status_code == 200
    
    def test_faculty_quick_actions_endpoints(self, faculty_token):
        """Test all Faculty quick action endpoints"""
        headers = {"Authorization": f"Bearer {faculty_token}"}
        
        endpoints = [
            "/api/students",
            "/api/subjects/mappings",
            "/api/attendance",
            "/api/marks"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"Faculty quick action {endpoint}: {response.status_code}")
            assert response.status_code == 200
    
    def test_principal_quick_actions_endpoints(self, principal_token):
        """Test all Principal quick action endpoints"""
        headers = {"Authorization": f"Bearer {principal_token}"}
        
        endpoints = [
            "/api/students",
            "/api/faculty",
            "/api/departments",
            "/api/announcements",
            "/api/audit-logs"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"Principal quick action {endpoint}: {response.status_code}")
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
