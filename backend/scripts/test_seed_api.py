import httpx
import asyncio

async def test_seed():
    print("--- Testing /api/seed Endpoint ---")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("http://localhost:8002/api/seed", timeout=10.0)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_seed())
