# Endpoint Inventory (Source of Truth)

Generated from `backend/server.py` route decorators.

## WebSocket
- `GET` (websocket): `/ws/{user_id}`

## API (`/api` prefix)

### Auth
- `POST` `/auth/register`
- `POST` `/auth/login`
- `GET` `/auth/me`

### Departments
- `POST` `/departments`
- `GET` `/departments`
- `GET` `/departments/{dept_id}`
- `PUT` `/departments/{dept_id}`
- `DELETE` `/departments/{dept_id}`

### Students
- `POST` `/students`
- `GET` `/students`
- `GET` `/students/{student_id}`
- `GET` `/students/me/profile`
- `PUT` `/students/{student_id}`
- `DELETE` `/students/{student_id}`
- `POST` `/students/enhanced`
- `PUT` `/students/{student_id}/profile`
- `GET` `/students/{student_id}/full-profile`
- `GET` `/students/{student_id}/documents`
- `POST` `/upload/document/{student_id}`

### Faculty
- `POST` `/faculty`
- `GET` `/faculty`
- `GET` `/faculty/me/profile`
- `PUT` `/faculty/{faculty_id}/class-incharge`
- `PUT` `/faculty/{faculty_id}`
- `DELETE` `/faculty/{faculty_id}`

### Subjects
- `POST` `/subjects`
- `GET` `/subjects`
- `POST` `/subjects/mapping`
- `GET` `/subjects/mappings`
- `PUT` `/subjects/{subject_id}`
- `DELETE` `/subjects/{subject_id}`

### Attendance
- `POST` `/attendance`
- `POST` `/attendance/bulk`
- `GET` `/attendance`
- `GET` `/attendance/summary/{student_id}`
- `POST` `/upload/attendance`

### Marks / CGPA
- `POST` `/marks`
- `POST` `/marks/bulk`
- `GET` `/marks`
- `PUT` `/marks/{marks_id}/lock`
- `GET` `/marks/cgpa/{student_id}`
- `POST` `/cgpa/calculate`
- `POST` `/cgpa/calculate-enhanced`
- `GET` `/cgpa/recalculate/{student_id}`
- `GET` `/cgpa/history`
- `GET` `/cgpa/overall`

### Fees
- `POST` `/fees/structure`
- `GET` `/fees/structure`
- `PUT` `/fees/structure/{fee_id}`
- `DELETE` `/fees/structure/{fee_id}`
- `POST` `/fees/create-order`
- `POST` `/fees/verify-payment`
- `GET` `/fees/payments`
- `GET` `/fees/pending`
- `POST` `/fees/initiate-manual-payment`
- `POST` `/fees/upload-screenshot/{payment_id}`
- `GET` `/fees/pending-verification`
- `PUT` `/fees/verify-screenshot/{payment_id}`
- `GET` `/fees/receipt/{payment_id}`
- `GET` `/fees/analytics`
- `GET` `/fees/analytics/export-pdf`

### Mail
- `POST` `/mail`
- `GET` `/mail/inbox`
- `GET` `/mail/sent`
- `GET` `/mail/drafts`
- `PUT` `/mail/{mail_id}/read`
- `PUT` `/mail/{mail_id}/archive`
- `GET` `/mail/users`

### Documents (Requests workflow)
- `POST` `/documents/request`
- `GET` `/documents/requests`
- `GET` `/documents/requests/{request_id}`
- `PUT` `/documents/requests/{request_id}/verify`
- `PUT` `/documents/requests/{request_id}/faculty-verify`
- `PUT` `/documents/requests/{request_id}/approve`
- `PUT` `/documents/requests/{request_id}/sign`
- `PUT` `/documents/requests/{request_id}/reject`

### Announcements
- `POST` `/announcements`
- `GET` `/announcements`
- `PUT` `/announcements/{ann_id}`
- `DELETE` `/announcements/{ann_id}`
- `GET` `/admin/announcements`

### Grievances
- `POST` `/grievances`
- `GET` `/grievances`
- `GET` `/grievances/{grievance_id}`
- `PUT` `/grievances/{grievance_id}`
- `DELETE` `/grievances/{grievance_id}`
- `GET` `/grievances/all`
- `PUT` `/grievances/{grievance_id}/forward`
- `PUT` `/grievances/{grievance_id}/resolve`
- `PUT` `/grievances/{grievance_id}/assign`
- `PUT` `/grievances/{grievance_id}/escalate`
- `POST` `/grievances/{grievance_id}/comment`
- `GET` `/grievances/{grievance_id}/comments`

### Leave Requests
- `POST` `/leave-requests`
- `GET` `/leave-requests`
- `PUT` `/leave-requests/{request_id}/approve`

### Settings / Profile
- `GET` `/settings`
- `PUT` `/settings`
- `POST` `/change-password`
- `GET` `/profile`
- `GET` `/preferences`
- `PUT` `/preferences`

### Uploads / Files
- `POST` `/upload/students`
- `POST` `/upload/marks`
- `GET` `/files/{folder}/{filename}`

### Audit Logs
- `GET` `/audit-logs`
- `GET` `/audit-logs/export`

### AI / Analytics
- `GET` `/ai/risk-score/{student_id}`
- `GET` `/ai/department-risks`
- `GET` `/analytics/dashboard`
- `GET` `/analytics/fees`
- `GET` `/analytics/attendance`
- `GET` `/analytics/risks`
- `GET` `/analytics/department/{dept_id}`

### Admissions
- `POST` `/admissions`
- `GET` `/admissions`
- `PUT` `/admissions/{app_id}/verify`
- `PUT` `/admissions/{app_id}/hod-approve`
- `PUT` `/admissions/{app_id}/principal-approve`

### Notifications / Automation
- `POST` `/notifications/automated-check`
- `POST` `/notifications`
- `GET` `/notifications/my`
- `PUT` `/notifications/{notification_id}/read`
- `PUT` `/notifications/mark-all-read`
- `DELETE` `/notifications/{notification_id}`
- `POST` `/automation/trigger`

### Chatbot
- `POST` `/chatbot/message`
- `GET` `/chatbot/sessions`
- `DELETE` `/chatbot/session/{session_id}`

### Timetable
- `POST` `/timetable/manual`
- `PUT` `/timetable/manual/{entry_id}`
- `DELETE` `/timetable/manual/{entry_id}`
- `GET` `/timetable/today`

### Seed
- `POST` `/seed`

