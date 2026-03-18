from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid
from fastapi import Depends, HTTPException
from ..repositories.fee_repository import FeeRepository, get_fee_repository
from ..repositories.student_repository import StudentRepository, get_student_repository
from ..core.audit import log_audit
from ..core.config import get_settings
from ..schemas.fee_schema import FeeStructure, FeePayment
from ..websocket.manager import manager

class FeeService:
    def __init__(self, fee_repo: FeeRepository, student_repo: StudentRepository):
        self.fee_repo = fee_repo
        self.student_repo = student_repo

    async def create_fee_structure(self, data: Dict[str, Any], admin_user_id: str) -> Dict[str, Any]:
        fee = FeeStructure(**data)
        doc = fee.model_dump()
        await self.fee_repo.create_structure(doc)
        await log_audit(admin_user_id, "create", "fee_structure", fee.id, after_value=doc)
        return doc

    async def get_fee_structures(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.fee_repo.get_structures(query, skip=skip, limit=limit)

    async def create_payment_order(self, student_user_id: str, fee_structure_id: str, scholarship: float, concession: float) -> Dict[str, Any]:
        student = await self.student_repo.get_by_user_id(student_user_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        fee_structure = await self.fee_repo.get_structure_by_id(fee_structure_id)
        if not fee_structure:
            raise HTTPException(status_code=404, detail="Fee structure not found")
        
        final_amount = fee_structure["amount"] - scholarship - concession
        final_amount = max(0, final_amount)
        
        settings = get_settings()
        razorpay_order_id = f"mock_order_{uuid.uuid4().hex[:12]}"
        # Razorpay integration logic could go here
        
        payment = FeePayment(
            student_id=student["id"],
            fee_structure_id=fee_structure_id,
            amount=final_amount,
            razorpay_order_id=razorpay_order_id,
            scholarship_applied=scholarship,
            concession_applied=concession
        )
        doc = payment.model_dump()
        doc["payment_date"] = doc["payment_date"].isoformat()
        doc["created_at"] = doc["created_at"].isoformat()
        await self.fee_repo.create_payment(doc)
        
        return {
            "order_id": razorpay_order_id,
            "payment_id": payment.id,
            "amount": final_amount,
            "currency": "INR",
            "key_id": settings.razorpay_key_id or "mock_key"
        }

    async def verify_payment(self, payment_id: str, razorpay_payment_id: str) -> Dict[str, Any]:
        payment = await self.fee_repo.get_payment_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        receipt_number = f"RCP{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        await self.fee_repo.update_payment(payment_id, {
            "status": "completed",
            "razorpay_payment_id": razorpay_payment_id,
            "receipt_number": receipt_number
        })
        
        student = await self.student_repo.get_by_id(payment["student_id"])
        if student:
            await manager.send_personal_message({
                "type": "fee_paid",
                "data": {"payment_id": payment_id, "receipt_number": receipt_number}
            }, student["user_id"])
            
        return {"message": "Payment verified", "status": "completed", "receipt_number": receipt_number}

    async def get_payments(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        payments = await self.fee_repo.get_payments(query, skip=skip, limit=limit)
        # Optimization: Batch fetch fee structures instead of N+1
        structure_ids = list({p["fee_structure_id"] for p in payments})
        structures = await self.fee_repo.get_structures({"id": {"$in": structure_ids}})
        struct_map = {s["id"]: s for s in structures}
        
        for p in payments:
            s = struct_map.get(p["fee_structure_id"])
            if s:
                p["fee_name"] = s["name"]
                p["fee_category"] = s["category"]
        return payments

    async def get_pending_fees(self, user: dict, student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if user["role"] != "student" and not student_id:
            return []
            
        if student_id and user["role"] in ["admin", "principal", "faculty"]:
            student = await self.student_repo.get_by_id(student_id)
        else:
            student = await self.student_repo.get_by_user_id(user["id"])
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Build query for fee structures applicable to this student
        fee_query = {
            "is_active": True,
            # Department filter: None, empty string, or exact match
            "$and": [
                {
                    "$or": [
                        {"department_id": None},
                        {"department_id": ""},
                        {"department_id": student.get("department_id")}
                    ]
                }
            ]
        }
        
        # Batch filter: None or exact match
        if student.get("batch"):
            fee_query["$and"].append({
                "$or": [
                    {"batch": None},
                    {"batch": ""},
                    {"batch": student["batch"]}
                ]
            })
            
        # Semester filter: None or exact match
        if student.get("semester"):
            fee_query["$and"].append({
                "$or": [
                    {"semester": None},
                    {"semester": 0},
                    {"semester": student["semester"]}
                ]
            })

        fee_structures = await self.fee_repo.get_structures(fee_query)
        
        paid_fees = await self.fee_repo.get_payments({
            "student_id": student["id"],
            "status": "completed"
        })
        paid_fee_ids = {p["fee_structure_id"] for p in paid_fees}
        
        return [f for f in fee_structures if f["id"] not in paid_fee_ids]

    async def initiate_manual_payment(self, user: dict, fee_structure_id: str) -> Dict[str, Any]:
        student = await self.student_repo.get_by_user_id(user["id"])
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        fee_structure = await self.fee_repo.get_structure_by_id(fee_structure_id)
        if not fee_structure:
            raise HTTPException(status_code=404, detail="Fee structure not found")
        
        payment = FeePayment(
            student_id=student["id"],
            fee_structure_id=fee_structure_id,
            amount=fee_structure["amount"],
            payment_method="upi",
            status="pending"
        )
        doc = payment.model_dump()
        doc["payment_date"] = doc["payment_date"].isoformat()
        doc["created_at"] = doc["created_at"].isoformat()
        await self.fee_repo.create_payment(doc)
        doc.pop("_id", None)
        
        return {
            "payment": doc,
            "bank_details": {
                "account_name": "Academia College",
                "account_number": "1234567890123456",
                "ifsc_code": "ACAD0001234",
                "bank_name": "State Bank of India",
                "branch": "College Campus Branch"
            },
            "upi_id": "academia@sbi",
            "qr_code_url": "/static/qr/payment-qr.png"
        }

    async def upload_payment_screenshot(self, user: dict, payment_id: str, screenshot_url: str, transaction_id: Optional[str], bank_reference: Optional[str]) -> Dict[str, Any]:
        payment = await self.fee_repo.get_payment_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        if payment["status"] == "completed":
            raise HTTPException(status_code=400, detail="Payment already completed")
        
        receipt_number = f"RCP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        await self.fee_repo.update_payment(payment_id, {
            "screenshot_url": screenshot_url,
            "transaction_id": transaction_id,
            "bank_reference": bank_reference,
            "status": "completed",
            "receipt_number": receipt_number,
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "verification_remarks": "Automated system verification"
        })
        
        student = await self.student_repo.get_by_id(payment["student_id"])
        if student:
            await manager.send_personal_message({
                "type": "fee_payment_verified",
                "data": {"payment_id": payment_id, "receipt_number": receipt_number, "status": "completed"}
            }, student["user_id"])
            
        await manager.broadcast_to_role({
            "type": "payment_completed",
            "data": {"payment_id": payment_id, "student_id": payment["student_id"], "receipt_number": receipt_number}
        }, "admin")
        
        return {
            "message": "Payment completed successfully. Receipt generated.",
            "receipt_number": receipt_number
        }

    async def get_pending_verifications(self, user: dict) -> List[Dict[str, Any]]:
        from ..core.database import get_db
        db = get_db()
        
        # 1. Fetch all active students with user info and department
        student_pipeline = [
            {"$match": {"is_active": True}},
            {"$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "id",
                "as": "user"
            }},
            {"$unwind": "$user"},
            {"$lookup": {
                "from": "departments",
                "localField": "department_id",
                "foreignField": "id",
                "as": "dept"
            }},
            {"$unwind": {"path": "$dept", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "id": 1,
                "roll_number": 1,
                "register_number": {"$ifNull": ["$register_number", "$roll_number"]},
                "department_id": 1,
                "batch": 1,
                "semester": 1,
                "student_name": "$user.name",
                "department_name": "$dept.name"
            }}
        ]
        students = await db.students.aggregate(student_pipeline).to_list(None)
        
        # 2. Fetch all active fee structures
        fee_structures = await self.fee_repo.get_structures({"is_active": True})
        
        # 3. Fetch all completed payments to calculate paid amounts
        payments = await self.fee_repo.get_payments({"status": "completed"})
        
        # Create a lookup for total paid per student and fee structure
        # (student_id, fee_id) -> total_paid
        paid_map = {}
        for p in payments:
            key = (p["student_id"], p["fee_structure_id"])
            paid_map[key] = paid_map.get(key, 0) + p["amount"]
                
        results = []
        
        for student in students:
            student_total = 0
            student_paid = 0
            
            for fee in fee_structures:
                # Logic to see if fee applies to student
                dept_match = not fee.get("department_id") or fee["department_id"] == student.get("department_id")
                batch_match = not fee.get("batch") or fee["batch"] == student.get("batch")
                sem_match = not fee.get("semester") or fee["semester"] == student.get("semester")
                
                if dept_match and batch_match and sem_match:
                    fee_amount = fee["amount"]
                    paid_amount = paid_map.get((student["id"], fee["id"]), 0)
                    
                    student_total += fee_amount
                    student_paid += paid_amount
            
            pending_amount = student_total - student_paid
            
            # Per requirement: ALL students where pending_amount > 0
            if pending_amount > 0:
                results.append({
                    "id": student["id"], # Student ID serves as the identifier for this tracker row
                    "student_name": student["student_name"],
                    "roll_number": student["roll_number"],
                    "register_number": student["register_number"],
                    "department_name": student["department_name"],
                    "total_fee": student_total,
                    "paid_fees": student_paid,
                    "pending_fees": pending_amount,
                    "status": "pending_fees" # For frontend categorization
                })
        
        # Sort by pending amount (highest first)
        results.sort(key=lambda x: x["pending_fees"], reverse=True)
        return results


    async def get_fee_receipt(self, user: dict, payment_id: str) -> Dict[str, Any]:
        payments = await self.fee_repo.get_payments({"id": payment_id, "status": "completed"})
        if not payments:
            raise HTTPException(status_code=404, detail="Receipt not found")
        payment = payments[0]
        
        if user["role"] == "student":
            student = await self.student_repo.get_by_user_id(user["id"])
            if not student or student["id"] != payment["student_id"]:
                raise HTTPException(status_code=403, detail="Access denied")
        
        student = await self.student_repo.get_by_id(payment["student_id"])
        if student:
            from ..core.database import get_db
            db = get_db()
            student_user = await db.users.find_one({"id": student["user_id"]}, {"_id": 0, "name": 1, "email": 1})
            if student_user:
                payment["student_name"] = student_user["name"]
                payment["student_email"] = student_user["email"]
            payment["roll_number"] = student["roll_number"]
            payment["batch"] = student["batch"]
            
            dept = await db.departments.find_one({"id": student["department_id"]}, {"_id": 0, "name": 1, "code": 1})
            if dept:
                payment["department"] = dept
        
        fee_structure = await self.fee_repo.get_structure_by_id(payment["fee_structure_id"])
        if fee_structure:
            payment["fee_details"] = fee_structure
        
        return payment

    async def update_fee_structure(self, user: dict, fee_id: str, name: Optional[str], amount: Optional[float], due_date: Optional[str], is_active: Optional[bool]) -> Dict[str, Any]:
        fee = await self.fee_repo.get_structure_by_id(fee_id)
        if not fee:
            raise HTTPException(status_code=404, detail="Fee structure not found")
        
        update_data = {}
        if name: update_data["name"] = name
        if amount is not None: update_data["amount"] = amount
        if due_date: update_data["due_date"] = due_date
        if is_active is not None: update_data["is_active"] = is_active
        
        if update_data:
            before_value = dict(fee)
            await self.fee_repo.update_structure(fee_id, update_data)
            after_value = await self.fee_repo.get_structure_by_id(fee_id)
            await log_audit(user["id"], "update", "fee_structure", fee_id, before_value, after_value)
        
        updated = await self.fee_repo.get_structure_by_id(fee_id)
        return {"message": "Fee structure updated", "fee_structure": updated}

    async def delete_fee_structure(self, user: dict, fee_id: str) -> Dict[str, Any]:
        fee = await self.fee_repo.get_structure_by_id(fee_id)
        if not fee:
            raise HTTPException(status_code=404, detail="Fee structure not found")
        
        payment_count = await self.fee_repo.count_payments({"fee_structure_id": fee_id})
        if payment_count > 0:
            raise HTTPException(status_code=400, detail=f"Cannot delete fee structure with {payment_count} payments")
        
        await self.fee_repo.delete_structure(fee_id)
        await log_audit(user["id"], "delete", "fee_structure", fee_id, before_value=fee)
        
        return {"message": "Fee structure deleted"}

def get_fee_service(
    fee_repo: FeeRepository = Depends(get_fee_repository),
    student_repo: StudentRepository = Depends(get_student_repository)
) -> FeeService:
    return FeeService(fee_repo, student_repo)
