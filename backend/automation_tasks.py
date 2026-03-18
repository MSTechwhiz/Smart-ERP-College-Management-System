import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from server import db, manager

async def create_system_notification(user_id: str, title: str, message: str, n_type: str = "automated", priority: str = "normal"):
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "message": message,
        "notification_type": n_type,
        "priority": priority,
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification)
    # Try to send real-time
    try:
        await manager.send_personal_message({"type": "notification", "data": notification}, user_id)
    except:
        pass

async def check_attendance_shortage(threshold: float = 75.0):
    """Check for students with attendance below threshold"""
    students = await db.students.find({}, {"_id": 0, "id": 1, "user_id": 1, "name": 1}).to_list(None)
    for student in students:
        total = await db.attendance.count_documents({"student_id": student["id"]})
        if total > 0:
            present = await db.attendance.count_documents({"student_id": student["id"], "status": "present"})
            percentage = (present / total) * 100
            if percentage < threshold:
                await create_system_notification(
                    student["user_id"],
                    "Attendance Shortage Warning",
                    f"Your current attendance is {percentage:.1f}%, which is below the required {threshold}%. Please attend classes regularly.",
                    "attendance_warning",
                    "high"
                )

async def check_fee_dues():
    """Check for students with pending fee payments"""
    # This is a simplified check. Real implementation would match fee_structures with students
    fee_structures = await db.fee_structures.find({}, {"_id": 0}).to_list(None)
    for fee in fee_structures:
        query = {}
        if fee.get("department_id"): query["department_id"] = fee["department_id"]
        if fee.get("batch"): query["batch"] = fee["batch"]
        
        students = await db.students.find(query, {"_id": 0, "id": 1, "user_id": 1}).to_list(None)
        for student in students:
            # Check if verified payment exists for this fee
            payment = await db.fee_payments.find_one({
                "student_id": student["id"],
                "fee_structure_id": fee["id"],
                "status": "verified"
            })
            if not payment:
                await create_system_notification(
                    student["user_id"],
                    "Fee Due Reminder",
                    f"A fee payment of {fee.get('amount', 0)} for '{fee.get('name', 'Semester Fees')}' is pending. Please clear it at the earliest.",
                    "fee_due",
                    "high"
                )

async def check_performance_warnings(min_cgpa: float = 6.0):
    """Check for students with CGPA below minimum threshold"""
    students = await db.students.find({"cgpa": {"$lt": min_cgpa}}, {"_id": 0, "id": 1, "user_id": 1, "cgpa": 1}).to_list(None)
    for student in students:
        await create_system_notification(
            student["user_id"],
            "Performance Warning",
            f"Your current CGPA is {student['cgpa']:.2f}, which is below the recommended {min_cgpa}. We suggest meeting your academic advisor.",
            "performance_warning",
            "normal"
        )

async def check_academic_deadlines():
    """Check for upcoming deadlines in announcements"""
    now = datetime.now(timezone.utc)
    soon = now + timedelta(days=3)
    
    # Simple check in announcements for keywords like 'deadline' or 'due'
    announcements = await db.announcements.find({
        "is_deleted": {"$ne": True},
        "content": {"$regex": "deadline|due date|last date", "$options": "i"}
    }).to_list(None)
    
    for ann in announcements:
        # If the announcement was recently published, it might be relevant
        pub_date = datetime.fromisoformat(ann["publish_date"].replace('Z', '+00:00'))
        if now - pub_date < timedelta(days=1):
            # Notify targeted roles
            roles = ann.get("target_roles", [])
            query = {}
            if roles:
                query["role"] = {"$in": roles}
            
            users = await db.users.find(query, {"id": 1}).to_list(None)
            for user in users:
                await create_system_notification(
                    user["id"],
                    "Upcoming Deadline Alert",
                    f"Reminder: {ann['title']} mentions an upcoming deadline. Please check the announcement for details.",
                    "deadline_alert",
                    "normal"
                )

async def run_all_automation():
    """Run all automated checks"""
    await check_attendance_shortage()
    await check_fee_dues()
    await check_performance_warnings()
    await check_academic_deadlines()
    return {"message": "Automation tasks completed"}
