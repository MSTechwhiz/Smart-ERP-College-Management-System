from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid

class Marks(BaseModel):
    model_config = ConfigDict(extra="ignore", protected_namespaces=())
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    subject_id: str
    academic_year: str
    semester: int
    cia1: Optional[float] = None
    cia2: Optional[float] = None
    cia3: Optional[float] = None
    cia4: Optional[float] = None
    model_exam: Optional[float] = None
    assignment: Optional[float] = None
    lab: Optional[float] = None
    semester_exam: Optional[float] = None
    total: Optional[float] = None
    grade: Optional[str] = None
    grade_point: Optional[float] = None
    is_locked: bool = False
    updated_by: str = ""
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MarksCreate(BaseModel):
    student_id: str
    subject_id: str
    academic_year: str
    semester: int
    exam_type: str  # cia1, cia2, cia3, cia4, model_exam, assignment, lab, semester_exam
    marks: float

class BulkMarksCreate(BaseModel):
    subject_id: str
    academic_year: str
    semester: int
    exam_type: str
    records: List[dict]  # [{"student_id": "...", "marks": 85}]
