from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from ..core.database import get_db
from ..websocket.manager import manager
from ..schemas.fee_notification_schema import FeeNotificationLog
from ..repositories.fee_repository import FeeRepository, get_fee_repository
from ..repositories.student_repository import StudentRepository, get_student_repository
from ..utils.sms_service import SMSService
from ..utils.whatsapp_service import WhatsAppService
from ..utils.email_service import send_email_notification
from ..utils.demo_email_service import send_demo_fee_email
import asyncio
from fastapi import Depends
import logging

logger = logging.getLogger(__name__)

# Demo Student Configuration
DEMO_STUDENTS = {
    "mobiles": ["8667781655", "8838216441"],
    "names": ["Sanjay M", "J Dhanush", "Sanjay", "Dhanush"]
}

class FeeNotificationService:
    def __init__(self, fee_repo: FeeRepository, student_repo: StudentRepository):
        self.fee_repo = fee_repo
        self.student_repo = student_repo

    async def send_fee_reminders(self, manual: bool = False) -> Dict[str, Any]:
        db = get_db()
        now = datetime.now(timezone.utc)
        
        # Determine target dates (for demo, we want to match our demo fee)
        # Today, Tomorrow, Day After
        today_str = now.strftime("%Y-%m-%d")
        tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        day_after_str = (now + timedelta(days=2)).strftime("%Y-%m-%d")
        relevant_dates = [today_str, tomorrow_str, day_after_str]
        
        # 1. Find active fee structures due within window
        fee_structures = await self.fee_repo.get_structures({
            "is_active": True,
            "due_date": {"$in": relevant_dates}
        })
        
        notifications_sent = []
        
        # DEMO MODE GUARANTEED EMAIL (Requirement: Instant real email to Sanjay M)
        demo_email_sent = False
        if manual:
            # Send real email to demo student instantly for live demonstration
            # We use a placeholder amount/due_date or use one from fee_structures if available
            first_fee = fee_structures[0] if fee_structures else {}
            sample_amount = first_fee.get("amount", 50000.0)
            sample_due_date = first_fee.get("due_date", (now + timedelta(days=2)).strftime("%Y-%m-%d"))
            
            demo_email_sent = await asyncio.to_thread(
                send_demo_fee_email, 
                "Sanjay M", 
                "msanjayit@gmail.com", 
                sample_amount,
                sample_due_date
            )
        
        demo_students_to_notify = []
        for fee in fee_structures:
            # ... [Existing pipeline logic for finding students - abbreviated here for brevity in replacement but I will include it all in my tool call] ...
            # I will actually include the full logic to avoid breaking the file.
            query = {"is_active": True}
            if manual:
                query["$or"] = [
                    {"mobile_number": {"$in": DEMO_STUDENTS["mobiles"]}},
                    {"name": {"$in": DEMO_STUDENTS["names"]}}
                ]
                query["department_id"] = "IT"
            else:
                if fee.get("department_id"): query["department_id"] = fee["department_id"]
                if fee.get("batch"): query["batch"] = fee["batch"]
                if fee.get("semester"): query["semester"] = fee["semester"]
            
            pipeline = [
                {"$match": query},
                {"$lookup": {
                    "from": "fee_payments",
                    "let": {"sid": "$id"},
                    "pipeline": [
                        {"$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$student_id", "$$sid"]},
                                    {"$eq": ["$fee_structure_id", fee["id"]]},
                                    {"$eq": ["$status", "completed"]}
                                ]
                            }
                        }}
                    ],
                    "as": "payment"
                }},
                {"$match": {"payment": {"$size": 0}}},
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
                    "user_id": 1,
                    "name": "$user.name",
                    "email": "$user.email",
                    "mobile_number": 1,
                    "roll_number": 1,
                    "department": "$dept.name"
                }}
            ]
            
            async for student in db.students.aggregate(pipeline):
                demo_students_to_notify.append({
                    "student": student,
                    "fee": fee
                })

        # Process Notifications (Bulk preferred for Fast2SMS Developer Route)
        if manual and demo_students_to_notify:
            all_mobiles = [s["student"].get("mobile_number") for s in demo_students_to_notify if s["student"].get("mobile_number")]
            unique_mobiles = ",".join(list(set(all_mobiles)))
            
            fee_sample = demo_students_to_notify[0]["fee"]
            bulk_message = f"AcademiaOS Fee Reminder: Your semester fee Rs.{fee_sample['amount']} is pending. Please complete payment before the due date."
            
            # 1. Send Bulk SMS
            sms_delivered = await SMSService.send_sms(unique_mobiles, bulk_message)
            
            for item in demo_students_to_notify:
                student = item["student"]
                fee = item["fee"]
                
                # 2. Send WhatsApp
                wa_sent = await WhatsAppService.send_whatsapp(student["mobile_number"], bulk_message)
                
                # 3. Send Email
                student_email = student.get("email")
                email_sent = False
                if student_email:
                    email_subject = "Fee Payment Reminder"
                    email_body = (
                        f"Dear {student['name']},\n\n"
                        f"This is a reminder that your fee payment of ₹{fee['amount']} is pending.\n\n"
                        f"Department: {student.get('department', 'N/A')}\n"
                        f"Register Number: {student['roll_number']}\n\n"
                        f"Please complete the payment at the earliest.\n\n"
                        f"Regards\n"
                        f"AcademiaOS Admin"
                    )
                    email_sent = await asyncio.to_thread(send_email_notification, student_email, email_subject, email_body)

                sms_status = "SMS Delivered" if sms_delivered else "SMS Failed"
                wa_status = "WhatsApp Sent" if wa_sent else "WhatsApp Failed"
                em_status = "Email Sent" if email_sent else ("Email Skipped" if not student_email else "Email Failed")
                
                final_status = f"{sms_status}, {wa_status}, {em_status}"
                
                log_entry = FeeNotificationLog(
                    student_id=student["id"],
                    student_name=student["name"],
                    mobile_number=student.get("mobile_number"),
                    email_address=student_email,
                    fee_name=fee["name"],
                    amount=fee["amount"],
                    status=final_status,
                    sms_status=sms_status,
                    whatsapp_status=wa_status,
                    email_status=em_status,
                    message=bulk_message
                )
                await db.fee_notification_logs.insert_one(log_entry.model_dump())
                
                notifications_sent.append({
                    "student_name": student["name"],
                    "roll_number": student["roll_number"],
                    "amount": fee["amount"],
                    "fee_name": fee["name"],
                    "status": final_status,
                    "mobile": student.get("mobile_number"),
                    "email": student_email
                })
        else:
            for item in demo_students_to_notify:
                student = item["student"]
                fee = item["fee"]
                notif_message = f"AcademiaOS Fee Reminder: Your semester fee ₹{fee['amount']} is pending. Please complete payment before the due date."
                is_demo = student.get("mobile_number") in DEMO_STUDENTS["mobiles"] or student.get("name") in DEMO_STUDENTS["names"]
                
                sms_delivered = await SMSService.send_sms(student["mobile_number"], notif_message) if is_demo else False
                wa_sent = await WhatsAppService.send_whatsapp(student["mobile_number"], notif_message) if is_demo else False
                
                student_email = student.get("email")
                email_sent = False
                if student_email:
                    email_subject = "Fee Payment Reminder"
                    email_body = (
                        f"Dear {student['name']},\n\n"
                        f"This is a reminder that your fee payment of ₹{fee['amount']} is pending.\n\n"
                        f"Department: {student.get('department', 'N/A')}\n"
                        f"Register Number: {student['roll_number']}\n\n"
                        f"Please complete the payment at the earliest.\n\n"
                        f"Regards\n"
                        f"AcademiaOS Admin"
                    )
                    email_sent = await asyncio.to_thread(send_email_notification, student_email, email_subject, email_body)

                sms_status = "SMS Delivered" if sms_delivered else "SMS Failed"
                wa_status = "WhatsApp Sent" if wa_sent else "WhatsApp Failed"
                em_status = "Email Sent" if email_sent else ("Email Skipped" if not student_email else "Email Failed")
                final_status = f"{sms_status}, {wa_status}, {em_status}"
                
                await db.fee_notification_logs.insert_one(FeeNotificationLog(
                    student_id=student["id"],
                    student_name=student["name"],
                    mobile_number=student.get("mobile_number"),
                    email_address=student_email,
                    fee_name=fee["name"],
                    amount=fee["amount"],
                    status=final_status,
                    sms_status=sms_status,
                    whatsapp_status=wa_status,
                    email_status=em_status,
                    message=notif_message
                ).model_dump())
                
                notifications_sent.append({
                    "student_name": student["name"],
                    "roll_number": student["roll_number"],
                    "amount": fee["amount"],
                    "fee_name": fee["name"],
                    "status": final_status,
                    "mobile": student.get("mobile_number"),
                    "email": student_email
                })
                
        return {
            "notified_students": notifications_sent,
            "demo_email_sent": demo_email_sent,
            "demo_recipient": "Sanjay M (msanjayit@gmail.com)" if demo_email_sent else None
        }

    async def get_notification_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        db = get_db()
        return await db.fee_notification_logs.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(None)

def get_fee_notification_service(
    fee_repo: FeeRepository = Depends(get_fee_repository),
    student_repo: StudentRepository = Depends(get_student_repository)
) -> FeeNotificationService:
    return FeeNotificationService(fee_repo, student_repo)
