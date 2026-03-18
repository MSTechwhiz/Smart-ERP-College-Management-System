from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid

class FeeStructure(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str  # tuition, exam, transport, hostel, semester, misc
    amount: float
    department_id: Optional[str] = None
    batch: Optional[str] = None
    semester: Optional[int] = None
    due_date: Optional[str] = None
    is_active: bool = True

class FeePayment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    receipt_number: str = Field(default_factory=lambda: f"RCP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}")
    student_id: str
    fee_structure_id: str
    amount: float
    payment_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payment_method: str = "upi"  # upi, bank_transfer, cash, online
    transaction_id: Optional[str] = None
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    status: str = "pending"  # pending, screenshot_uploaded, verifying, verified, completed, rejected, failed
    screenshot_url: Optional[str] = None
    bank_reference: Optional[str] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    verification_remarks: Optional[str] = None
    scholarship_applied: float = 0.0
    concession_applied: float = 0.0
    late_fee: float = 0.0
    fine_amount: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FeePaymentCreate(BaseModel):
    fee_structure_id: str
    amount: float
    payment_method: str = "upi"
    transaction_id: Optional[str] = None
    bank_reference: Optional[str] = None
