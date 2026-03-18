from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import uuid
from .database import get_db
from ..websocket.manager import manager

async def send_automated_notification(user_id: str, title: str, message: str, n_type: str = "System", priority: str = "normal"):
    db = get_db()
    # Get user role for notification
    user = await db.users.find_one({"id": user_id}, {"role": 1})
    if not user: return
    
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "role": user["role"],
        "type": n_type, # Announcement, Academic, Administrative, System
        "title": title,
        "message": message,
        "priority": priority,
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification)
    try:
        await manager.send_personal_message({"type": "notification", "data": notification}, user_id)
    except:
        pass

async def check_all_automations():
    """Run all background automation checks using optimized aggregations"""
    db = get_db()
    
    # 1. Attendance Shortage (< 75%)
    attendance_pipeline = [
        {"$group": {
            "_id": "$student_id",
            "total": {"$sum": 1},
            "present": {"$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}}
        }},
        {"$addFields": {
            "percentage": {"$multiply": [{"$divide": ["$present", "$total"]}, 100]}
        }},
        {"$match": {"percentage": {"$lt": 75.0}}},
        {"$lookup": {
            "from": "students",
            "localField": "_id",
            "foreignField": "id",
            "as": "student"
        }},
        {"$unwind": "$student"},
        {"$project": {"user_id": "$student.user_id", "percentage": 1}}
    ]
    
    async for row in db.attendance.aggregate(attendance_pipeline):
        await send_automated_notification(
            row["user_id"],
            "Attendance Alert",
            f"Your attendance is currently {row['percentage']:.1f}%. Please attend more classes to maintain eligibility.",
            "attendance_warning",
            "high"
        )

    # 2. Fee Dues (Proximity reminders: <= 2 days)
    now = datetime.now(timezone.utc)
    relevant_dates = [
        now.strftime("%Y-%m-%d"),
        (now + timedelta(days=1)).strftime("%Y-%m-%d"),
        (now + timedelta(days=2)).strftime("%Y-%m-%d")
    ]
    
    fee_structures = await db.fee_structures.find({
        "is_active": True,
        "due_date": {"$in": relevant_dates}
    }).to_list(None)
    
    for fee in fee_structures:
        # Match students applicable for this fee
        query = {"is_active": True}
        if fee.get("department_id"): query["department_id"] = fee["department_id"]
        if fee.get("batch"): query["batch"] = fee["batch"]
        if fee.get("semester"): query["semester"] = fee["semester"]
        
        fee_pipeline = [
            {"$match": query},
            {"$lookup": {
                "from": "fee_payments",
                "let": {"sid": "$id"},
                "pipeline": [
                    {"$match": {
                        "$expr": {
                            "$and": [
                                {"$eq": ["$student_id", "$$sid"]},
                                {"$eq": ["$fee_structure_id", fee["id"]]},
                                {"$eq": ["$status", "completed"]}
                            ]
                        }
                    }}
                ],
                "as": "payment"
            }},
            {"$match": {"payment": {"$size": 0}}},
            {"$project": {"user_id": 1, "name": 1, "mobile_number": 1, "roll_number": 1, "id": 1}}
        ]
        
        async for student in db.students.aggregate(fee_pipeline):
            # Send System Notification
            await send_automated_notification(
                student["user_id"],
                "Urgent: Fee Due Tomorrow" if fee["due_date"] != relevant_dates[2] else "Fee Due Soon",
                f"Payment of ₹{fee.get('amount', 0)} for {fee.get('name')} is pending. Due Date: {fee['due_date']}",
                "fee_due",
                "high"
            )
            
            # Log for the new Fee Notification Log (SMS simulation)
            from .utils import str_uuid # Assuming we have a way to generate ID if needed, or just insert
            import uuid
            
            log_entry = {
                "id": str(uuid.uuid4()),
                "student_id": student["id"],
                "student_name": student.get("name", "Unknown"),
                "mobile_number": student.get("mobile_number"),
                "fee_name": fee["name"],
                "amount": fee["amount"],
                "status": "Sent",
                "message": f"AcademiaOS Fee Reminder: Dear {student.get('name')}, your fee ₹{fee['amount']} is pending. Due: {fee['due_date']}",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.fee_notification_logs.insert_one(log_entry)

    # 3. Performance Warning (< 6.0 CGPA)
    async for student in db.students.find({"cgpa": {"$lt": 6.0}, "is_active": True}, {"user_id": 1, "cgpa": 1}):
        await send_automated_notification(
            student["user_id"],
            "Academic Performance Warning",
            f"Your current CGPA is {student.get('cgpa', 0):.2f}. We recommend extra coaching or meeting with your mentor.",
            "performance_warning",
            "normal"
        )

    # 4. Academic Deadlines (Upcoming in next 3 days)
    now = datetime.now(timezone.utc)
    soon = now + timedelta(days=3)
    
    # Check announcements for deadlines
    deadlines = await db.announcements.find({
        "is_deleted": {"$ne": True},
        "content": {"$regex": "deadline|last date|due date", "$options": "i"}
    }).to_list(None)
    
    for dead in deadlines:
        pub_date_str = dead["publish_date"]
        if 'Z' in pub_date_str:
            pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
        else:
            pub_date = datetime.fromisoformat(pub_date_str)
            
        if now - pub_date < timedelta(days=2):
            roles = dead.get("target_roles", [])
            user_query = {}
            if roles: user_query["role"] = {"$in": roles}
            
            target_users = await db.users.find(user_query, {"id": 1}).to_list(None)
            for target in target_users:
                await send_automated_notification(
                    target["id"],
                    "Upcoming Deadline",
                    f"Reminder: {dead['title']} mentions an upcoming deadline. Don't miss it!",
                    "deadline_alert",
                    "normal"
                )
