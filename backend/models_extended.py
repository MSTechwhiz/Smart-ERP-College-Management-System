# Extended Models for College ERP System
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid

# ==================== EXTENDED STUDENT MODEL ====================

class StudentPersonalInfo(BaseModel):
    """Extended personal information for student"""
    photo_url: Optional[str] = None
    aadhaar_number: Optional[str] = None
    passport_number: Optional[str] = None
    gender: Optional[str] = None  # male, female, other
    date_of_birth: Optional[str] = None
    blood_group: Optional[str] = None
    nationality: str = "Indian"
    religion: Optional[str] = None
    caste: Optional[str] = None
    category: Optional[str] = None  # general, obc, sc, st
    mother_tongue: Optional[str] = None
    
class StudentFamilyInfo(BaseModel):
    """Family information"""
    father_name: Optional[str] = None
    father_occupation: Optional[str] = None
    father_phone: Optional[str] = None
    father_email: Optional[str] = None
    mother_name: Optional[str] = None
    mother_occupation: Optional[str] = None
    mother_phone: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    guardian_relation: Optional[str] = None
    annual_income: Optional[float] = None
    income_category: Optional[str] = None  # below_1L, 1L_3L, 3L_6L, above_6L

class StudentAddressInfo(BaseModel):
    """Address information"""
    permanent_address: Optional[str] = None
    permanent_city: Optional[str] = None
    permanent_state: Optional[str] = None
    permanent_pincode: Optional[str] = None
    current_address: Optional[str] = None
    current_city: Optional[str] = None
    current_state: Optional[str] = None
    current_pincode: Optional[str] = None

class StudentAcademicHistory(BaseModel):
    """Previous academic records"""
    tenth_board: Optional[str] = None
    tenth_year: Optional[int] = None
    tenth_percentage: Optional[float] = None
    tenth_school: Optional[str] = None
    twelfth_board: Optional[str] = None
    twelfth_year: Optional[int] = None
    twelfth_percentage: Optional[float] = None
    twelfth_school: Optional[str] = None
    twelfth_stream: Optional[str] = None  # science, commerce, arts
    diploma_course: Optional[str] = None
    diploma_year: Optional[int] = None
    diploma_percentage: Optional[float] = None
    diploma_institution: Optional[str] = None
    entrance_exam: Optional[str] = None  # JEE, TNEA, etc.
    entrance_score: Optional[float] = None
    entrance_rank: Optional[int] = None

class StudentAdministrativeInfo(BaseModel):
    """Administrative details"""
    admission_quota: Optional[str] = None  # management, government, nri
    admission_type: Optional[str] = None  # regular, lateral
    hostel_status: Optional[str] = None  # day_scholar, hosteller
    hostel_room: Optional[str] = None
    transport_status: Optional[str] = None  # own, college_bus
    bus_route: Optional[str] = None
    scholarship_name: Optional[str] = None
    scholarship_amount: Optional[float] = None

class ExtendedStudent(BaseModel):
    """Complete extended student model"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    roll_number: str
    department_id: str
    batch: str
    semester: int = 1
    section: Optional[str] = None
    mentor_id: Optional[str] = None
    cgpa: float = 0.0
    regulation: str = "R2023"
    admission_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # Extended fields
    personal_info: StudentPersonalInfo = Field(default_factory=StudentPersonalInfo)
    family_info: StudentFamilyInfo = Field(default_factory=StudentFamilyInfo)
    address_info: StudentAddressInfo = Field(default_factory=StudentAddressInfo)
    academic_history: StudentAcademicHistory = Field(default_factory=StudentAcademicHistory)
    administrative_info: StudentAdministrativeInfo = Field(default_factory=StudentAdministrativeInfo)
    # Status flags
    is_active: bool = True
    has_backlogs: bool = False
    backlog_count: int = 0
    disciplinary_records: List[dict] = []

class StudentUpdateRequest(BaseModel):
    """Request model for updating student profile"""
    personal_info: Optional[StudentPersonalInfo] = None
    family_info: Optional[StudentFamilyInfo] = None
    address_info: Optional[StudentAddressInfo] = None
    academic_history: Optional[StudentAcademicHistory] = None
    administrative_info: Optional[StudentAdministrativeInfo] = None

# ==================== ADMISSION WORKFLOW MODEL ====================

class AdmissionApplication(BaseModel):
    """Admission application model"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # Applicant details
    applicant_name: str
    applicant_email: EmailStr
    applicant_phone: str
    date_of_birth: str
    gender: str
    category: str = "general"
    # Academic details
    department_id: str
    course: str = "B.Tech"
    admission_type: str = "regular"  # regular, lateral
    quota: str = "government"  # government, management, nri
    # Previous academics
    tenth_percentage: float
    twelfth_percentage: Optional[float] = None
    diploma_percentage: Optional[float] = None
    entrance_exam: Optional[str] = None
    entrance_score: Optional[float] = None
    entrance_rank: Optional[int] = None
    # Reference
    reference_name: Optional[str] = None
    reference_phone: Optional[str] = None
    reference_relation: Optional[str] = None
    # Workflow status
    status: str = "submitted"  # submitted, office_verified, hod_approved, principal_approved, rejected
    rejection_reason: Optional[str] = None
    # Timestamps
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    office_verified_at: Optional[datetime] = None
    office_verified_by: Optional[str] = None
    hod_reviewed_at: Optional[datetime] = None
    hod_reviewed_by: Optional[str] = None
    principal_approved_at: Optional[datetime] = None
    principal_approved_by: Optional[str] = None
    # Auto-created student ID
    created_student_id: Optional[str] = None

class AdmissionApplicationCreate(BaseModel):
    """Create admission application"""
    applicant_name: str
    applicant_email: EmailStr
    applicant_phone: str
    date_of_birth: str
    gender: str
    category: str = "general"
    department_id: str
    course: str = "B.Tech"
    admission_type: str = "regular"
    quota: str = "government"
    tenth_percentage: float
    twelfth_percentage: Optional[float] = None
    diploma_percentage: Optional[float] = None
    entrance_exam: Optional[str] = None
    entrance_score: Optional[float] = None
    entrance_rank: Optional[int] = None
    reference_name: Optional[str] = None
    reference_phone: Optional[str] = None
    reference_relation: Optional[str] = None

# ==================== GRIEVANCE EXTENDED MODEL ====================

class GrievanceComment(BaseModel):
    """Comment on grievance"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    grievance_id: str
    user_id: str
    user_name: str
    user_role: str
    comment: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GrievanceCommentCreate(BaseModel):
    """Create grievance comment"""
    comment: str

# ==================== FEE CONCESSION WORKFLOW ====================

class FeeConcessionRequest(BaseModel):
    """Fee concession request"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    fee_structure_id: str
    requested_amount: float
    reason: str
    supporting_documents: List[str] = []
    status: str = "submitted"  # submitted, office_verified, hod_approved, principal_approved, rejected
    approved_amount: Optional[float] = None
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    office_verified_at: Optional[datetime] = None
    office_verified_by: Optional[str] = None
    hod_approved_at: Optional[datetime] = None
    hod_approved_by: Optional[str] = None
    principal_approved_at: Optional[datetime] = None
    principal_approved_by: Optional[str] = None

class FeeConcessionCreate(BaseModel):
    """Create fee concession request"""
    fee_structure_id: str
    requested_amount: float
    reason: str

# ==================== CGPA CALCULATOR CONFIG ====================

class RegulationConfig(BaseModel):
    """CGPA regulation configuration"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    regulation_code: str  # R2023, R2020, etc.
    name: str
    grade_scale: Dict[str, float]  # {"O": 10, "A+": 9, ...}
    pass_grade: str = "P"
    pass_grade_point: float = 4.0
    max_credits_per_semester: int = 30
    min_cgpa_for_pass: float = 5.0
    backlog_rules: Dict[str, Any] = {}
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== INSTALLMENT PAYMENT ====================

class FeeInstallment(BaseModel):
    """Fee installment plan"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    fee_structure_id: str
    total_amount: float
    installment_count: int
    installments: List[Dict[str, Any]] = []  # [{"number": 1, "amount": 25000, "due_date": "...", "status": "pending/paid"}]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== OFFICE WORKFLOW STATUS ====================

WORKFLOW_STATUSES = {
    "admission": ["submitted", "office_verified", "hod_approved", "principal_approved", "rejected"],
    "document": ["submitted", "office_verified", "hod_approved", "principal_signed", "generated", "rejected"],
    "grievance": ["open", "in_progress", "resolved", "escalated", "closed"],
    "concession": ["submitted", "office_verified", "hod_approved", "principal_approved", "rejected"]
}
