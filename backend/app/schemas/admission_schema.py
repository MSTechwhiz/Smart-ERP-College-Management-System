from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional
import uuid

class AdmissionApplicationCreate(BaseModel):
    applicant_name: str
    applicant_email: EmailStr
    applicant_phone: str
    date_of_birth: str
    gender: str
    category: str = "general"
    department_id: str
    course: str = "B.Tech"
    quota_type: str = "Counseling"  # Counseling, Management
    scholarship_type: str = "None"  # BC, MBC, SC, First Graduate, None
    marks_10: float
    marks_12: Optional[float] = None
    diploma_percentage: Optional[float] = None
    certificates_upload: List[str] = []  # List of file paths/URLs
    status: str = "Pending"
    verified_by: Optional[str] = None
    admission_date: Optional[str] = None
