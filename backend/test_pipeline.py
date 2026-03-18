import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def run_pipeline():
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
    
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    db = client[os.getenv("DATABASE_NAME", "college_db")]
    
    match_query = {}

    pipeline = [
        {"$match": match_query},
        {"$lookup": {
            "from": "attendance",
            "localField": "id",
            "foreignField": "student_id",
            "as": "attendance"
        }},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "id",
            "as": "user"
        }},
        {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "student_id": "$id",
            "roll_number": "$roll_number",
            "name": {"$ifNull": ["$user.name", "Unknown"]},
            "email": {"$ifNull": ["$user.email", ""]},
            "cgpa": {"$ifNull": ["$cgpa", 0]},
            "total_att": {"$size": "$attendance"},
            "present_att": {
                "$size": {
                    "$filter": {
                        "input": "$attendance",
                        "as": "a",
                        "cond": {"$in": ["$$a.status", ["present", "od"]]}
                    }
                }
            }
        }},
        {"$project": {
            "student_id": 1, "roll_number": 1, "name": 1, "email": 1, "cgpa": 1,
            "attendance_percentage": {
                "$cond": [
                    {"$gt": ["$total_att", 0]},
                    {"$multiply": [{"$divide": ["$present_att", "$total_att"]}, 100]},
                    100
                ]
            }
        }},
        # Add risk scoring logic in projection
        {"$addFields": {
            "risk_score": {
                "$add": [
                    {"$cond": [{"$lt": ["$attendance_percentage", 75]}, 40, {"$cond": [{"$lt": ["$attendance_percentage", 85]}, 20, 0]}]},
                    {"$cond": [{"$lt": ["$cgpa", 5]}, 40, {"$cond": [{"$lt": ["$cgpa", 6]}, 20, 0]}]}
                ]
            }
        }},
        {"$match": {"risk_score": {"$gt": 20}}},
        {"$addFields": {
            "risk_level": {
                "$cond": [{"$gte": ["$risk_score", 60]}, "high", {"$cond": [{"$gte": ["$risk_score", 40]}, "medium", "low"]}]
            },
            "risk_factors": {
                "$setUnion": [
                    {"$cond": [{"$lt": ["$attendance_percentage", 75]}, ["Low attendance"], {"$cond": [{"$lt": ["$attendance_percentage", 85]}, ["Moderate attendance"], []]}]},
                    {"$cond": [{"$lt": ["$cgpa", 5]}, ["Low CGPA"], {"$cond": [{"$lt": ["$cgpa", 6]}, ["Moderate CGPA"], []]}]}
                ]
            }
        }},
        {"$sort": {"risk_score": -1}},
        {"$project": {
            "student_id": 1, "roll_number": 1, "name": 1, "email": 1, 
            "attendance_percentage": {"$round": ["$attendance_percentage", 2]},
            "cgpa": 1, "risk_score": 1, "risk_level": 1, "risk_factors": 1
        }}
    ]
    
    try:
        results = await db.students.aggregate(pipeline).to_list(None)
        print("Success!", results)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(run_pipeline())
