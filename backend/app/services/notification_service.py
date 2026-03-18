from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid
from fastapi import Depends, HTTPException, BackgroundTasks
from ..repositories.notification_repository import NotificationRepository, get_notification_repository
from ..repositories.student_repository import StudentRepository, get_student_repository
from ..repositories.attendance_repository import AttendanceRepository, get_attendance_repository
from ..repositories.fee_repository import FeeRepository, get_fee_repository
from ..websocket.manager import manager

class NotificationService:
    def __init__(
        self, 
        notification_repo: NotificationRepository,
        student_repo: StudentRepository,
        attendance_repo: AttendanceRepository,
        fee_repo: FeeRepository
    ):
        self.notification_repo = notification_repo
        self.student_repo = student_repo
        self.attendance_repo = attendance_repo
        self.fee_repo = fee_repo

    async def create_notification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        notification = {
            "id": str(uuid.uuid4()),
            "is_read": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            **data
        }
        await self.notification_repo.create(notification)
        await manager.send_personal_message({"type": "notification", "data": notification}, data["user_id"])
        return notification

    async def run_automated_checks(self) -> int:
        notifications_sent = 0
        # 1. Attendance Shortage
        students = await self.student_repo.get_students_with_users({})
        for s in students:
            summary = await self.attendance_repo.get_summary(s["id"])
            for sub in summary:
                if sub["total"] >= 10 and sub["percentage"] < 75:
                    await self.create_notification({
                        "user_id": s["user_id"],
                        "title": "Attendance Shortage Warning",
                        "message": f"Your attendance in {sub['subject_name']} is {sub['percentage']}%. Required: 75%",
                        "notification_type": "warning",
                        "priority": "high"
                    })
                    notifications_sent += 1

        # 2. Fee Dues
        pending_fees = await self.fee_repo.get_payments({"status": {"$ne": "completed"}})
        for f in pending_fees:
            student = await self.student_repo.get_by_id(f["student_id"])
            if student:
                await self.create_notification({
                    "user_id": student["user_id"],
                    "title": "Fee Payment Reminder",
                    "message": f"Pending fee payment: ₹{f['amount']}",
                    "notification_type": "fee",
                    "priority": "normal"
                })
                notifications_sent += 1
        return notifications_sent

    async def get_my_notifications(self, user_id: str, unread_only: bool = False, limit: int = 50) -> List[Dict[str, Any]]:
        query = {"user_id": user_id}
        if unread_only: query["is_read"] = False
        return await self.notification_repo.list_notifications(query, limit)

    async def mark_read(self, notification_id: str, user_id: str) -> bool:
        return await self.notification_repo.update({"id": notification_id, "user_id": user_id}, {"is_read": True}) > 0

    async def mark_all_read(self, user_id: str) -> int:
        return await self.notification_repo.update({"user_id": user_id, "is_read": False}, {"is_read": True})

    async def delete_notification(self, notification_id: str, user_id: str) -> bool:
        return await self.notification_repo.delete(notification_id, user_id)

def get_notification_service(
    notification_repo: NotificationRepository = Depends(get_notification_repository),
    student_repo: StudentRepository = Depends(get_student_repository),
    attendance_repo: AttendanceRepository = Depends(get_attendance_repository),
    fee_repo: FeeRepository = Depends(get_fee_repository)
) -> NotificationService:
    return NotificationService(notification_repo, student_repo, attendance_repo, fee_repo)
