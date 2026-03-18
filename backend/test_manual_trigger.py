import requests
import json

def test_trigger():
    # We need an admin login token. Let's assume the admin is admin@academia.edu / admin123
    # Or we can just use the internal endpoint if we bypass auth, but it's better to test the route.
    
    # Since I'm an agent, I might not have the cleartext password, but I can check the database for an admin email.
    # However, for a quick verification, I can just call the service method directly in a python script if I want to bypass HTTP.
    # But testing the HTTP endpoint is better.
    
    base_url = "http://localhost:8002/api"
    
    # 1. Login as Admin
    login_data = {"email": "admin@academia.edu", "password": "admin123"}
    login_res = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return
        
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Trigger Reminders
    print("Triggering fee reminders...")
    trigger_res = requests.post(f"{base_url}/fees/send-reminders", headers=headers)
    
    if trigger_res.status_code == 200:
        print("Success!")
        print(json.dumps(trigger_res.json(), indent=2))
    else:
        print(f"Trigger failed: {trigger_res.status_code} - {trigger_res.text}")

    # 3. Check History
    print("\nFetching notification history...")
    history_res = requests.get(f"{base_url}/fees/notifications/history", headers=headers)
    if history_res.status_code == 200:
        print(f"Found {len(history_res.json())} logs in history.")
        # Print the first few
        for log in history_res.json()[:5]:
            print(f"- {log['student_name']}: {log['fee_name']} - {log['status']} at {log['created_at']}")
    else:
        print(f"History fetch failed: {history_res.text}")

if __name__ == "__main__":
    test_trigger()
