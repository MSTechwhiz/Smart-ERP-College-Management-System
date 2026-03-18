from typing import List, Optional, Dict, Any
from ..core.database import get_db
from pymongo import InsertOne, UpdateOne

class UploadRepository:
    def __init__(self):
        self.db = get_db()

    async def get_student_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.students.find_one({"id": student_id}, {"_id": 0})

    async def insert_student_document(self, doc_record: Dict[str, Any]) -> str:
        await self.db.student_documents.insert_one(doc_record)
        doc_record.pop("_id", None)
        return doc_record["id"]

    async def update_student_profile_doc(self, student_id: str, document_type: str, file_path: str) -> bool:
        field_map = {
            "tenth_certificate": "tenth_certificate.certificate_url",
            "twelfth_certificate": "twelfth_certificate.certificate_url",
            "id_proof": "identity_proof.document_url"
        }
        field = field_map.get(document_type)
        if not field:
            return False
        
        result = await self.db.students.update_one(
            {"id": student_id},
            {"$set": {field: file_path}}
        )
        return result.modified_count > 0

    async def get_departments_map(self) -> Dict[str, str]:
        depts = await self.db.departments.find({}, {"id": 1, "code": 1}).to_list(None)
        return {d["code"]: d["id"] for d in depts}

    async def get_student_by_roll(self, roll_number: str) -> Optional[Dict[str, Any]]:
        return await self.db.students.find_one({"roll_number": roll_number}, {"_id": 0, "id": 1})

    async def get_subject_by_code(self, subject_code: str) -> Optional[Dict[str, Any]]:
        return await self.db.subjects.find_one({"code": subject_code}, {"_id": 0, "id": 1})

    async def get_marks_record(self, student_id: str, subject_id: str, academic_year: str, semester: int) -> Optional[Dict[str, Any]]:
        return await self.db.marks.find_one({
            "student_id": student_id,
            "subject_id": subject_id,
            "academic_year": academic_year,
            "semester": semester
        }, {"_id": 0})

    async def bulk_write_users_students(self, user_ops: List[InsertOne], student_ops: List[InsertOne]) -> bool:
        if user_ops:
            await self.db.users.bulk_write(user_ops, ordered=False)
        if student_ops:
            await self.db.students.bulk_write(student_ops, ordered=False)
        return True

    async def bulk_write_marks(self, marks_ops: List[Any]) -> bool:
        if marks_ops:
            await self.db.marks.bulk_write(marks_ops, ordered=False)
        return True

    async def bulk_write_attendance(self, attendance_ops: List[UpdateOne]) -> bool:
        if attendance_ops:
            await self.db.attendance.bulk_write(attendance_ops, ordered=False)
        return True

    async def create_notification(self, notif_data: Dict[str, Any]) -> str:
        await self.db.notifications.insert_one(notif_data)
        notif_data.pop("_id", None)
        return notif_data["id"]
