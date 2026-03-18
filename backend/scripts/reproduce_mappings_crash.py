import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_mappings_query():
    from app.core.database import connect_to_mongo, get_db
    from app.services.subject_service import get_subject_service
    from app.repositories.subject_repository import get_subject_repository
    
    await connect_to_mongo()
    db = get_db()
    
    repo = get_subject_repository(db)
    from app.services.subject_service import SubjectService
    service = SubjectService(repo)
    
    query = {
        "academic_year": "2024-25",
        "semester": 5
    }
    dept_id = "5e89fad5-8c4a-49ef-892f-6e9344efdc7f"
    
    print(f"Testing mappings query: {query}, dept_id={dept_id}")
    try:
        results = await service.get_mappings(query, department_id=dept_id)
        print(f"Success! Found {len(results)} results.")
    except Exception as e:
        print(f"CRASH in get_mappings:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mappings_query())
