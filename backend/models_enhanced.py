"""
Enhanced Models for College ERP System
Includes: Advanced Student Profile, Documents, Audit Logs, Notifications
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid

# ==================== ENHANCED STUDENT PROFILE ====================

class CertificateDetails(BaseModel):
    """10th/12th Certificate Details"""
    school_name: Optional[str] = None
    board: Optional[str] = None
    year_of_passing: Optional[int] = None
    total_marks: Optional[float] = None
    marks_obtained: Optional[float] = None
    percentage: Optional[float] = None
    cutoff: Optional[float] = None  # For 12th only
    certificate_url: Optional[str] = None

class IdentityProof(BaseModel):
    """Identity Proof Details"""
    id_type: Optional[str] = None  # aadhaar, pan, driving_license
    id_number: Optional[str] = None
    document_url: Optional[str] = None

class ParentDetails(BaseModel):
    """Parent/Guardian Details"""
    father_name: Optional[str] = None
    father_occupation: Optional[str] = None
    father_contact: Optional[str] = None
    mother_name: Optional[str] = None
    mother_occupation: Optional[str] = None
    mother_contact: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_contact: Optional[str] = None

class StudentProfile(BaseModel):
    """Extended Student Profile"""
    model_config = ConfigDict(extra="ignore")
    
    # Basic Information
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    roll_number: str
    register_number: Optional[str] = None
    department_id: str
    year: int = 1
    semester: int = 1
    section: Optional[str] = None
    batch: str
    
    # Personal Details
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    mobile_number: Optional[str] = None
    alternate_mobile: Optional[str] = None
    email: str
    
    # Address
    permanent_address: Optional[str] = None
    communication_address: Optional[str] = None
    
    # Academic Records
    tenth_certificate: Optional[CertificateDetails] = None
    twelfth_certificate: Optional[CertificateDetails] = None
    
    # Identity
    identity_proof: Optional[IdentityProof] = None
    
    # Additional Information
    community: Optional[str] = None
    scholarship_details: Optional[str] = None
    is_first_graduate: bool = False
    parent_details: Optional[ParentDetails] = None
    hostel_day_scholar: str = "day_scholar"  # hostel, day_scholar
    admission_type: Optional[str] = None  # management, government, counselling
    
    # Academic
    cgpa: float = 0.0
    regulation: str = "R2023"
    mentor_id: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    is_active: bool = True

class StudentProfileCreate(BaseModel):
    """Create Student Profile Request"""
    # Basic Information (Required)
    name: str
    email: EmailStr
    password: str
    roll_number: str
    department_id: str
    batch: str
    
    # Optional fields
    register_number: Optional[str] = None
    year: int = 1
    semester: int = 1
    section: Optional[str] = None
    
    # Personal Details
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    mobile_number: Optional[str] = None
    alternate_mobile: Optional[str] = None
    
    # Address
    permanent_address: Optional[str] = None
    communication_address: Optional[str] = None
    
    # 10th Certificate
    tenth_school_name: Optional[str] = None
    tenth_board: Optional[str] = None
    tenth_year: Optional[int] = None
    tenth_total_marks: Optional[float] = None
    tenth_marks_obtained: Optional[float] = None
    tenth_percentage: Optional[float] = None
    
    # 12th Certificate
    twelfth_school_name: Optional[str] = None
    twelfth_board: Optional[str] = None
    twelfth_year: Optional[int] = None
    twelfth_total_marks: Optional[float] = None
    twelfth_marks_obtained: Optional[float] = None
    twelfth_percentage: Optional[float] = None
    twelfth_cutoff: Optional[float] = None
    
    # Identity Proof
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    
    # Additional
    community: Optional[str] = None
    scholarship_details: Optional[str] = None
    is_first_graduate: bool = False
    hostel_day_scholar: str = "day_scholar"
    admission_type: Optional[str] = None
    
    # Parent Details
    father_name: Optional[str] = None
    father_occupation: Optional[str] = None
    father_contact: Optional[str] = None
    mother_name: Optional[str] = None
    mother_occupation: Optional[str] = None
    mother_contact: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_contact: Optional[str] = None
    
    # Academic
    regulation: str = "R2023"
    mentor_id: Optional[str] = None

class StudentProfileUpdate(BaseModel):
    """Update Student Profile Request"""
    name: Optional[str] = None
    register_number: Optional[str] = None
    year: Optional[int] = None
    semester: Optional[int] = None
    section: Optional[str] = None
    
    # Personal Details
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    mobile_number: Optional[str] = None
    alternate_mobile: Optional[str] = None
    
    # Address
    permanent_address: Optional[str] = None
    communication_address: Optional[str] = None
    
    # 10th Certificate
    tenth_school_name: Optional[str] = None
    tenth_board: Optional[str] = None
    tenth_year: Optional[int] = None
    tenth_total_marks: Optional[float] = None
    tenth_marks_obtained: Optional[float] = None
    tenth_percentage: Optional[float] = None
    
    # 12th Certificate
    twelfth_school_name: Optional[str] = None
    twelfth_board: Optional[str] = None
    twelfth_year: Optional[int] = None
    twelfth_total_marks: Optional[float] = None
    twelfth_marks_obtained: Optional[float] = None
    twelfth_percentage: Optional[float] = None
    twelfth_cutoff: Optional[float] = None
    
    # Identity Proof
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    
    # Additional
    community: Optional[str] = None
    scholarship_details: Optional[str] = None
    is_first_graduate: Optional[bool] = None
    hostel_day_scholar: Optional[str] = None
    admission_type: Optional[str] = None
    
    # Parent Details
    father_name: Optional[str] = None
    father_occupation: Optional[str] = None
    father_contact: Optional[str] = None
    mother_name: Optional[str] = None
    mother_occupation: Optional[str] = None
    mother_contact: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_contact: Optional[str] = None
    
    # Academic
    cgpa: Optional[float] = None
    mentor_id: Optional[str] = None

# ==================== AUDIT LOG ====================

class AuditLog(BaseModel):
    """Audit Log Entry"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_name: str
    role: str
    module: str  # students, faculty, fees, attendance, marks, etc.
    action: str  # create, update, delete, approve, reject, upload, bulk_insert
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== NOTIFICATIONS ====================

class Notification(BaseModel):
    """Notification Model"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    role: str # Requirement: role field
    type: str # Requirement: type field (Announcement, Academic, Administrative, System)
    title: str
    message: str
    is_read: bool = False
    priority: str = "normal"  # low, normal, high, urgent
    action_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

# ==================== FEES MANAGEMENT ====================

class FeesMaster(BaseModel):
    """Fee Structure Master"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str  # tuition, exam, lab, transport, hostel, misc
    amount: float
    department_id: Optional[str] = None  # null = all departments
    batch: Optional[str] = None
    semester: Optional[int] = None
    due_date: Optional[str] = None
    fine_per_day: float = 0.0
    max_fine: float = 0.0
    is_active: bool = True
    academic_year: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None

class FeesTransaction(BaseModel):
    """Fee Payment Transaction"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    fee_structure_id: str
    amount: float
    fine_amount: float = 0.0
    concession_amount: float = 0.0
    total_amount: float
    payment_method: str = "screenshot"  # screenshot, razorpay, cash, cheque
    transaction_id: Optional[str] = None
    screenshot_url: Optional[str] = None
    bank_reference: Optional[str] = None
    status: str = "pending"  # pending, screenshot_uploaded, verified, rejected
    payment_date: Optional[datetime] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    remarks: Optional[str] = None
    receipt_number: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FeesStatus(BaseModel):
    """Student Fee Status Summary"""
    student_id: str
    total_fees: float
    paid_amount: float
    pending_amount: float
    fine_amount: float
    concession_amount: float
    last_payment_date: Optional[datetime] = None

# ==================== TIMETABLE / TODAY CLASS ====================

class TimetableEntry(BaseModel):
    """Timetable Entry"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    faculty_id: str
    subject_id: str
    department_id: str
    section: str
    semester: int
    day_of_week: int  # 0=Monday, 6=Sunday
    period: int  # 1-8
    start_time: str  # HH:MM
    end_time: str  # HH:MM
    room_number: Optional[str] = None
    is_active: bool = True
    academic_year: str

class TodayClassManual(BaseModel):
    """Manual Today's Class Entry"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    faculty_id: str
    date: str  # YYYY-MM-DD
    period: int
    subject_id: Optional[str] = None
    topic: Optional[str] = None
    notes: Optional[str] = None
    is_completed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== USER PREFERENCES ====================

class UserPreference(BaseModel):
    """User Settings/Preferences"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    theme: str = "light"  # light, dark, system
    primary_color: str = "blue"  # blue, green, purple, orange, red
    sidebar_collapsed: bool = False
    notifications_enabled: bool = True
    email_notifications: bool = True
    sms_notifications: bool = False
    language: str = "en"
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== CGPA CALCULATION ====================

class CGPAEntry(BaseModel):
    """CGPA Calculator Entry"""
    subject_name: str
    credits: int
    grade: str  # O, A+, A, B+, B, C, U

class CGPACalculation(BaseModel):
    """CGPA Calculation Result"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    semester: int
    entries: List[CGPAEntry]
    sgpa: float
    total_credits: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Anna University Grade Points
ANNA_UNIVERSITY_GRADES = {
    "O": 10,
    "A+": 9,
    "A": 8,
    "B+": 7,
    "B": 6,
    "C": 5,
    "U": 0,
    "RA": 0,  # Re-appear
    "AB": 0,  # Absent
}

def calculate_sgpa(entries: List[CGPAEntry]) -> tuple:
    """Calculate SGPA based on Anna University system"""
    total_credits = 0
    weighted_sum = 0
    
    for entry in entries:
        grade_point = ANNA_UNIVERSITY_GRADES.get(entry.grade.upper(), 0)
        weighted_sum += grade_point * entry.credits
        total_credits += entry.credits
    
    if total_credits == 0:
        return 0.0, 0
    
    sgpa = round(weighted_sum / total_credits, 2)
    return sgpa, total_credits

# ==================== CHATBOT ====================

class ChatMessage(BaseModel):
    """Chat Message"""
    role: str  # user, assistant
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatSession(BaseModel):
    """Chat Session"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_role: str
    messages: List[ChatMessage] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== DOCUMENT STORAGE ====================

class StudentDocument(BaseModel):
    """Student Document Upload"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    document_type: str  # tenth_certificate, twelfth_certificate, id_proof, photo, other
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_verified: bool = False
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
