import asyncio
import httpx

async def test_api():
    async with httpx.AsyncClient() as client:
        # 1. Login
        login_resp = await client.post("http://localhost:8000/api/auth/login", json={
            "email": "principal@academia.edu",  # Default seed principal email usually
            "password": "Password123!", # We will try a few common ones
            "role": "principal"
        })
        
        if login_resp.status_code != 200:
            # Let's try admin if principal fails
            login_resp = await client.post("http://localhost:8000/api/auth/login", json={
                "email": "admin@college.edu",
                "password": "Password123!",
                "role": "admin"
            })
            
        print("Login Status:", login_resp.status_code)
        if login_resp.status_code != 200:
            print(login_resp.json())
            return
            
        token = login_resp.json().get("access_token")
        
        # 2. GET /api/analytics/risks
        risks_resp = await client.get("http://localhost:8000/api/analytics/risks", headers={
            "Authorization": f"Bearer {token}"
        })
        print("Risks Status:", risks_resp.status_code)
        print("Risks Body:", risks_resp.text)

if __name__ == "__main__":
    asyncio.run(test_api())
