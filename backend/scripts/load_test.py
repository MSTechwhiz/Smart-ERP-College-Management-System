from locust import HttpUser, task, between
import random

class AcademiaUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Mock login to get token (in real scenario, would use stored test accounts)
        self.token = "test-token"
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def view_dashboard(self):
        self.client.get("/api/v1/analytics/dashboard", headers=self.headers)

    @task(2)
    def list_students(self):
        self.client.get("/api/v1/students?limit=20", headers=self.headers)

    @task(2)
    def list_announcements(self):
        self.client.get("/api/v1/announcements", headers=self.headers)

    @task(1)
    def check_health(self):
        self.client.get("/health")
