from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid

class Subject(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    name: str
    department_id: str
    semester: int
    credits: int
    subject_type: str = "theory"  # theory, lab, project
    regulation: str = "R2023"

class SubjectCreate(BaseModel):
    code: str
    name: str
    department_id: str
    semester: int
    credits: int
    subject_type: str = "theory"
    regulation: str = "R2023"

class SubjectFacultyMapping(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject_id: str
    faculty_id: str
    section: str
    academic_year: str
    semester: int
    day: str  # Monday, Tuesday, etc.
    period: int  # 1-7
    start_time: str  # "09:00"
    end_time: str  # "10:00"

class SubjectFacultyMappingCreate(BaseModel):
    subject_id: str
    faculty_id: str
    section: str
    academic_year: str
    semester: int
    day: str
    period: int
    start_time: str
    end_time: str
