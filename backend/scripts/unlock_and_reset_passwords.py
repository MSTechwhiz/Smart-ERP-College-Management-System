"""
Unlock locked accounts and reset synced student passwords to FirstName@123 format.
Run from: d:\college2-main\  with: python backend/scripts/unlock_and_reset_passwords.py [email]
If email is provided, only that account is unlocked. Otherwise all synced students are reset.
"""
import asyncio
import sys
import os

sys.path.append(os.getcwd())

STANDARD_PASSWORD_SUFFIX = "@123"

async def get_db():
    try:
        from backend.app.core.database import connect_to_mongo, get_db as _get_db
        from backend.app.core.security import hash_password
    except ImportError:
        from app.core.database import connect_to_mongo, get_db as _get_db
        from app.core.security import hash_password
    await connect_to_mongo()
    return _get_db(), hash_password

def make_default_password(name: str) -> str:
    """Generate a default password: FirstName@123"""
    first = name.strip().split()[0].replace(",", "").replace(".", "")
    # Capitalize first letter
    first = first.capitalize()
    return f"{first}{STANDARD_PASSWORD_SUFFIX}"

async def unlock_account(email: str):
    """Clear the in-memory lockout cache for a specific email."""
    try:
        from backend.app.utils.cache import cache
    except ImportError:
        from app.utils.cache import cache
    lockout_key = f"lockout:{email}"
    attempts_key = f"attempts:{email}"
    await cache.delete(lockout_key)
    await cache.delete(attempts_key)
    print(f"Unlocked account: {email}")

async def reset_student_passwords(target_email: str = None):
    db, hash_password = await get_db()
    
    query = {"role": "student"}
    if target_email:
        query["email"] = target_email

    users = await db.users.find(query, {"_id": 0}).to_list(length=None)
    print(f"Found {len(users)} student user(s) to process.")

    reset_count = 0
    for u in users:
        name = u.get("name", "")
        email = u.get("email", "")
        if not name or not email:
            continue

        new_password = make_default_password(name)
        hashed = await hash_password(new_password)
        await db.users.update_one({"email": email}, {"$set": {"password": hashed}})
        
        # Also clear any lockout
        await unlock_account(email)
        
        print(f"  Reset: {email} → password: {new_password}")
        reset_count += 1

    print(f"\nDone! Reset {reset_count} student password(s).")
    print(f"Default password format: FirstName{STANDARD_PASSWORD_SUFFIX}  (e.g., Sanjay@123)")

async def main():
    target_email = sys.argv[1] if len(sys.argv) > 1 else None
    await reset_student_passwords(target_email)

if __name__ == "__main__":
    asyncio.run(main())
