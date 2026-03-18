#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

class CollegeERPTester:
    def __init__(self, base_url="https://college-preview-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tokens = {}  # Store tokens for each role
        self.test_users = {
            'principal': {'email': 'principal@academia.edu', 'password': 'principal123'},
            'admin': {'email': 'admin@academia.edu', 'password': 'admin123'},
            'hod': {'email': 'hod.cse@academia.edu', 'password': 'hod123'},
            'faculty': {'email': 'faculty@academia.edu', 'password': 'faculty123'},
            'student': {'email': 'student@academia.edu', 'password': 'student123'}
        }
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Optional[Dict] = None, headers: Optional[Dict] = None, 
                 role: Optional[str] = None) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if role and role in self.tokens:
            test_headers['Authorization'] = f'Bearer {self.tokens[role]}'

        self.tests_run += 1
        self.log(f"🔍 Testing {name}... ({method} {endpoint})")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ PASSED - {name} - Status: {response.status_code}")
            else:
                self.log(f"❌ FAILED - {name} - Expected {expected_status}, got {response.status_code}")
                self.log(f"   Response: {response.text[:200]}")
                self.failed_tests.append({
                    'name': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'response': response.text[:500]
                })

            try:
                return success, response.json() if response.text else {}
            except json.JSONDecodeError:
                return success, {'raw_response': response.text}

        except requests.RequestException as e:
            self.log(f"❌ FAILED - {name} - Network Error: {str(e)}")
            self.failed_tests.append({
                'name': name,
                'expected': expected_status,
                'actual': 'Network Error',
                'response': str(e)
            })
            return False, {}

    def authenticate_role(self, role: str) -> bool:
        """Authenticate and store token for a role"""
        if role not in self.test_users:
            self.log(f"❌ Unknown role: {role}")
            return False
        
        creds = self.test_users[role]
        success, response = self.run_test(
            f"Login as {role}",
            "POST", 
            "auth/login",
            200,
            data={
                "email": creds['email'],
                "password": creds['password'],
                "role": role
            }
        )
        
        if success and 'access_token' in response:
            self.tokens[role] = response['access_token']
            self.log(f"✅ Authentication successful for {role}")
            return True
        else:
            self.log(f"❌ Authentication failed for {role}")
            return False

    def test_health_check(self):
        """Test basic API connectivity"""
        self.log("=== Testing API Health ===")
        success, _ = self.run_test("API Health Check", "GET", "", 404)  # Root should return 404
        return success

    def test_authentication(self):
        """Test authentication for all roles"""
        self.log("=== Testing Authentication ===")
        auth_success = True
        
        for role in self.test_users.keys():
            if not self.authenticate_role(role):
                auth_success = False
        
        # Test invalid credentials
        success, _ = self.run_test(
            "Invalid login attempt",
            "POST",
            "auth/login", 
            401,
            data={"email": "wrong@email.com", "password": "wrong", "role": "student"}
        )
        
        return auth_success

    def test_user_profile_endpoints(self):
        """Test user profile endpoints"""
        self.log("=== Testing User Profile Endpoints ===")
        
        # Test /auth/me for each role
        for role in ['student', 'faculty', 'principal']:
            if role in self.tokens:
                self.run_test(f"Get {role} profile", "GET", "auth/me", 200, role=role)
        
        # Test student profile
        if 'student' in self.tokens:
            self.run_test("Get student profile", "GET", "students/me/profile", 200, role='student')
        
        # Test faculty profile
        if 'faculty' in self.tokens:
            self.run_test("Get faculty profile", "GET", "faculty/me/profile", 200, role='faculty')

    def test_student_dashboard_apis(self):
        """Test student dashboard related APIs"""
        self.log("=== Testing Student Dashboard APIs ===")
        
        if 'student' not in self.tokens:
            self.log("❌ Skipping student tests - no token")
            return
            
        # Test attendance
        self.run_test("Get student attendance", "GET", "attendance", 200, role='student')
        
        # Test marks
        self.run_test("Get student marks", "GET", "marks", 200, role='student')
        
        # Test announcements
        self.run_test("Get announcements", "GET", "announcements", 200, role='student')
        
        # Test pending fees
        self.run_test("Get pending fees", "GET", "fees/pending", 200, role='student')
        
        # Test fee payments
        self.run_test("Get fee payments", "GET", "fees/payments", 200, role='student')
        
        # Test mailbox
        self.run_test("Get inbox", "GET", "mail/inbox", 200, role='student')
        
        # Test document requests
        self.run_test("Get document requests", "GET", "documents/requests", 200, role='student')
        
        # Test grievances
        self.run_test("Get grievances", "GET", "grievances", 200, role='student')

    def test_principal_dashboard_apis(self):
        """Test principal dashboard APIs"""
        self.log("=== Testing Principal Dashboard APIs ===")
        
        if 'principal' not in self.tokens:
            self.log("❌ Skipping principal tests - no token")
            return
            
        # Test analytics - might not exist yet, expect 404 or implement mock
        self.run_test("Get dashboard analytics", "GET", "analytics/dashboard", 404, role='principal')
        
        # Test departments
        self.run_test("Get departments", "GET", "departments", 200, role='principal')
        
        # Test students list
        self.run_test("Get all students", "GET", "students", 200, role='principal')
        
        # Test faculty list
        self.run_test("Get all faculty", "GET", "faculty", 200, role='principal')
        
        # Test announcements
        self.run_test("Get announcements", "GET", "announcements", 200, role='principal')

    def test_admin_functions(self):
        """Test admin specific functions"""
        self.log("=== Testing Admin Functions ===")
        
        if 'admin' not in self.tokens:
            self.log("❌ Skipping admin tests - no token")
            return
            
        # Test bulk operations access
        self.run_test("Get students (admin)", "GET", "students", 200, role='admin')
        self.run_test("Get faculty (admin)", "GET", "faculty", 200, role='admin')
        
        # Test document verification workflow
        self.run_test("Get document requests (admin)", "GET", "documents/requests", 200, role='admin')

    def test_hod_functions(self):
        """Test HOD specific functions"""
        self.log("=== Testing HOD Functions ===")
        
        if 'hod' not in self.tokens:
            self.log("❌ Skipping HOD tests - no token")
            return
            
        # Test department specific access
        self.run_test("Get department students (HOD)", "GET", "students", 200, role='hod')
        self.run_test("Get department faculty (HOD)", "GET", "faculty", 200, role='hod')

    def test_faculty_functions(self):
        """Test faculty specific functions"""
        self.log("=== Testing Faculty Functions ===")
        
        if 'faculty' not in self.tokens:
            self.log("❌ Skipping faculty tests - no token")
            return
            
        # Test attendance and marks access
        self.run_test("Get attendance records", "GET", "attendance", 200, role='faculty')
        self.run_test("Get marks records", "GET", "marks", 200, role='faculty')

    def test_workflow_operations(self):
        """Test key workflow operations"""
        self.log("=== Testing Workflow Operations ===")
        
        # Test document request workflow (student submits)
        if 'student' in self.tokens:
            success, response = self.run_test(
                "Submit document request",
                "POST",
                "documents/request",
                200,
                data={"document_type": "bonafide", "remarks": "Test request"},
                role='student'
            )
        
        # Test grievance submission
        if 'student' in self.tokens:
            self.run_test(
                "Submit grievance",
                "POST", 
                "grievances",
                200,
                data={
                    "subject": "Test grievance",
                    "description": "This is a test grievance",
                    "category": "academic"
                },
                role='student'
            )
        
        # Test fee payment order creation
        if 'student' in self.tokens:
            # First get fee structures to find a valid ID
            success, fee_structures = self.run_test("Get fee structures", "GET", "fees/structure", 200, role='student')
            if success and fee_structures and len(fee_structures) > 0:
                fee_id = fee_structures[0].get('id')
                if fee_id:
                    self.run_test(
                        "Create fee payment order",
                        "POST",
                        "fees/create-order",
                        200,
                        data={"fee_structure_id": fee_id},
                        role='student'
                    )

    def test_role_based_access_control(self):
        """Test role-based access control"""
        self.log("=== Testing Role-Based Access Control ===")
        
        # Student trying to access admin endpoint should fail
        if 'student' in self.tokens:
            self.run_test(
                "Student accessing admin endpoint (should fail)",
                "GET",
                "students",  # Only admin/principal should access all students
                403,  # Should get forbidden or similar
                role='student'
            )
        
        # Faculty trying to access principal endpoints
        if 'faculty' in self.tokens:
            self.run_test(
                "Faculty accessing department creation (should fail)",
                "POST",
                "departments",
                403,
                data={"name": "Test Dept", "code": "TD"},
                role='faculty'
            )

    def test_data_seeding(self):
        """Test data seeding endpoint"""
        self.log("=== Testing Data Seeding ===")
        
        # Test seed endpoint - this should work without authentication
        success, response = self.run_test("Seed demo data", "POST", "seed", 200)
        return success

    def run_all_tests(self):
        """Run complete test suite"""
        self.log("🚀 Starting College ERP API Test Suite")
        self.log(f"📍 Testing against: {self.base_url}")
        
        # Test basic connectivity first
        if not self.test_health_check():
            self.log("❌ API connectivity failed - aborting tests")
            return False
        
        # Test data seeding (should be idempotent)
        self.test_data_seeding()
        
        # Test authentication
        if not self.test_authentication():
            self.log("❌ Authentication failed for multiple roles")
        
        # Test user profiles
        self.test_user_profile_endpoints()
        
        # Test role-specific functionalities
        self.test_student_dashboard_apis()
        self.test_principal_dashboard_apis()
        self.test_admin_functions()
        self.test_hod_functions()
        self.test_faculty_functions()
        
        # Test workflows
        self.test_workflow_operations()
        
        # Test security
        self.test_role_based_access_control()
        
        return True

    def print_summary(self):
        """Print test summary"""
        self.log("=" * 50)
        self.log("🏁 TEST SUMMARY")
        self.log("=" * 50)
        self.log(f"📊 Tests Run: {self.tests_run}")
        self.log(f"✅ Tests Passed: {self.tests_passed}")
        self.log(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        
        if self.failed_tests:
            self.log("\n🔍 FAILED TESTS DETAILS:")
            for i, test in enumerate(self.failed_tests[:10]):  # Show first 10 failures
                self.log(f"  {i+1}. {test['name']}")
                self.log(f"     Expected: {test['expected']}, Got: {test['actual']}")
                if len(test['response']) > 0:
                    self.log(f"     Response: {test['response'][:100]}...")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.log(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 70  # Consider 70% success as acceptable


def main():
    """Main test runner"""
    tester = CollegeERPTester()
    
    try:
        tester.run_all_tests()
        success = tester.print_summary()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        tester.log("⏹️ Test interrupted by user")
        return 1
    except Exception as e:
        tester.log(f"💥 Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())