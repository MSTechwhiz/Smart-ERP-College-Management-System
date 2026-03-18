import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.utils.demo_email_service import send_demo_fee_email

async def test_demo_email():
    print("--- Testing Demo Email Service ---")
    # This will attempt to send a real email using settings in .env
    success = send_demo_fee_email(
        "Sanjay M",
        "msanjayit@gmail.com",
        50000.0,
        "2026-03-20"
    )
    if success:
        print("SUCCESS: Demo email triggered.")
    else:
        print("FAILED: Demo email failed (Check .env credentials).")

if __name__ == "__main__":
    asyncio.run(test_demo_email())
