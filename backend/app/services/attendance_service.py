from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from fastapi import Depends
from ..repositories.attendance_repository import AttendanceRepository, get_attendance_repository
from ..repositories.student_repository import StudentRepository, get_student_repository
from ..websocket.manager import manager
from ..schemas.attendance_schema import Attendance, AttendanceCreate, BulkAttendanceCreate

class AttendanceService:
    def __init__(
        self, 
        attendance_repo: AttendanceRepository, 
        student_repo: StudentRepository
    ):
        self.attendance_repo = attendance_repo
        self.student_repo = student_repo

    async def mark_attendance(self, attendance_data: AttendanceCreate, user_id: str) -> Dict[str, Any]:
        attendance = Attendance(
            **attendance_data.model_dump(),
            marked_by=user_id
        )
        doc = attendance.model_dump()
        doc["marked_at"] = doc["marked_at"].isoformat()
        
        await self.attendance_repo.upsert_attendance(
            attendance_data.student_id, 
            attendance_data.subject_id, 
            attendance_data.date, 
            doc
        )
        
        # Send WebSocket notification
        student = await self.student_repo.get_by_id(attendance_data.student_id)
        if student:
            await manager.send_personal_message({
                "type": "attendance_updated",
                "data": {
                    "subject_id": attendance_data.subject_id, 
                    "date": attendance_data.date, 
                    "status": attendance_data.status
                }
            }, student["user_id"])
            
        return doc

    async def mark_bulk_attendance(self, bulk_data: BulkAttendanceCreate, user_id: str) -> Dict[str, Any]:
        records_to_upsert = []
        for record in bulk_data.records:
            attendance = Attendance(
                student_id=record["student_id"],
                subject_id=bulk_data.subject_id,
                date=bulk_data.date,
                status=record["status"],
                marked_by=user_id
            )
            doc = attendance.model_dump()
            doc["marked_at"] = doc["marked_at"].isoformat()
            records_to_upsert.append(doc)
            
        success_count = await self.attendance_repo.bulk_upsert_attendance(records_to_upsert)
        return {"message": f"Bulk attendance marked: {success_count} success", "success_count": success_count}

    async def get_attendance(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.attendance_repo.get_attendance(query, skip=skip, limit=limit)

    async def get_summary(self, student_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.attendance_repo.get_summary(student_id, skip=skip, limit=limit)

def get_attendance_service(
    attendance_repo: AttendanceRepository = Depends(get_attendance_repository),
    student_repo: StudentRepository = Depends(get_student_repository)
) -> AttendanceService:
    return AttendanceService(attendance_repo, student_repo)
