from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import get_settings


_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        settings = get_settings()
        _client = AsyncIOMotorClient(settings.mongo_url)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        settings = get_settings()
        _db = get_client()[settings.db_name]
    return _db


async def connect_to_mongo() -> None:
    global _client, _db
    if _client is None:
        settings = get_settings()
        _client = AsyncIOMotorClient(settings.mongo_url)
        _db = _client[settings.db_name]
        
        # Create indexes from legacy server.py
        await _db.users.create_index("email", unique=True)
        await _db.users.create_index("id", unique=True)
        await _db.students.create_index("roll_number", unique=True)
        await _db.students.create_index("user_id")
        await _db.faculty.create_index("employee_id", unique=True)
        await _db.faculty.create_index("user_id")
        await _db.departments.create_index("code", unique=True)
        await _db.subjects.create_index("code", unique=True)
        await _db.attendance.create_index([("student_id", 1), ("subject_id", 1), ("date", 1)])
        await _db.marks.create_index([("student_id", 1), ("subject_id", 1), ("academic_year", 1), ("semester", 1)])
        await _db.mails.create_index("to_user_id")
        await _db.mails.create_index("from_user_id")
        await _db.audit_logs.create_index("timestamp")
        await _db.audit_logs_enhanced.create_index([("timestamp", -1)])
        await _db.audit_logs_enhanced.create_index("module")
        await _db.audit_logs_enhanced.create_index("action")
        await _db.notifications.create_index([("user_id", 1), ("created_at", -1)])
        await _db.student_documents.create_index("student_id")
        await _db.cgpa_calculations.create_index("student_id")
        await _db.chat_sessions.create_index("user_id")
        await _db.today_classes.create_index([("faculty_id", 1), ("date", 1)])
        
        # New Roadmap Indexes
        await _db.students.create_index("department_id")
        await _db.faculty.create_index("department_id")
        await _db.fee_payments.create_index("student_id")


async def close_mongo_connection() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
    _client = None
    _db = None


