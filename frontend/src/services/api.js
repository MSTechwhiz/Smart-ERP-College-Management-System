import axios from "axios";
import { toast } from "sonner";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8002/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// REQUEST INTERCEPTOR
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// RESPONSE INTERCEPTOR
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      localStorage.removeItem("token");

      if (window.location.pathname !== "/") {
        window.location.href = "/";
      }
    }

    let message = 
      error.response?.data?.message || 
      error.response?.data?.detail;

    if (Array.isArray(message)) {
      message = message.map(err => err.msg || JSON.stringify(err)).join(', ');
    } else if (typeof message === 'object' && message !== null) {
      message = message.msg || JSON.stringify(message);
    }

    message = message || error.message || "Unexpected error occurred";

    // Update the error object to contain the sanitized message
    if (error.response?.data) {
      if (error.response.data.detail) error.response.data.detail = message;
      if (error.response.data.message) error.response.data.message = message;
    }

    if (error.response?.status !== 401) {
      toast.error(message);
    }

    console.error("API Error:", {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
    });

    return Promise.reject(error);
  }
);

export default api;

/* ---------------- AUTH ---------------- */
export const authAPI = {
  login: (data) => api.post("/auth/login", data),
  register: (data) => api.post("/auth/register", data),
  getMe: () => api.get("/auth/me"),
};

/* ---------------- DEPARTMENTS ---------------- */
export const departmentAPI = {
  getAll: () => api.get("/departments"),
  getOne: (id) => api.get(`/departments/${id}`),
  create: (data) => api.post("/departments", data),
  update: (id, data) => api.put(`/departments/${id}`, null, { params: data }),
  delete: (id) => api.delete(`/departments/${id}`),
};

/* ---------------- STUDENTS ---------------- */
export const studentAPI = {
  getAll: (params) => api.get("/students", { params }),
  getOne: (id) => api.get(`/students/${id}`),
  getMyProfile: () => api.get("/students/me/profile"),
  create: (data) => api.post("/students", data),
  update: (id, data) => api.put(`/students/${id}`, null, { params: data }),
  delete: (id) => api.delete(`/students/${id}`),
};

/* ---------------- FACULTY ---------------- */
export const facultyAPI = {
  getAll: (params) => api.get("/faculty", { params }),
  getMyProfile: () => api.get("/faculty/me/profile"),
  create: (data) => api.post("/faculty", data),
  update: (id, data) => api.put(`/faculty/${id}`, null, { params: data }),
  delete: (id) => api.delete(`/faculty/${id}`),
  assignClassIncharge: (facultyId, inchargeClass) =>
    api.put(`/faculty/${facultyId}/class-incharge?incharge_class=${inchargeClass}`),
};

/* ---------------- SUBJECTS ---------------- */
export const subjectAPI = {
  getAll: (params) => api.get("/subjects", { params }),
  create: (data) => api.post("/subjects", data),
  update: (id, data) => api.put(`/subjects/${id}`, null, { params: data }),
  delete: (id) => api.delete(`/subjects/${id}`),
  createMapping: (data) => api.post("/subjects/mapping", data),
  getMappings: (params) => api.get("/subjects/mappings", { params }),
  getStudentTimetable: () => api.get("/subjects/student-timetable"),
};

/* ---------------- ATTENDANCE ---------------- */
export const attendanceAPI = {
  mark: (data) => api.post("/attendance", data),
  markBulk: (data) => api.post("/attendance/bulk", data),
  getAll: (params) => api.get("/attendance", { params }),
  getSummary: (studentId) => api.get(`/attendance/summary/${studentId}`),
};

/* ---------------- MARKS ---------------- */
export const marksAPI = {
  enter: (data) => api.post("/marks", data),
  enterBulk: (data) => api.post("/marks/bulk", data),
  getAll: (params) => api.get("/marks", { params }),
  lock: (marksId) => api.put(`/marks/${marksId}/lock`),
  getCGPA: (studentId) => api.get(`/marks/cgpa/${studentId}`),
};

/* ---------------- CGPA ---------------- */
export const cgpaAPI = {
  calculate: (entries, semester, save = false) => api.post("/cgpa/calculate-enhanced", { entries, semester, save }),
  getHistory: () => api.get("/cgpa/history"),
  getOverall: () => api.get("/cgpa/overall"),
  recalculate: (studentId) => api.get(`/cgpa/recalculate/${studentId}`),
};

/* ---------------- FEES ---------------- */
export const feeAPI = {
  getStructures: (params) => api.get("/fees/structure", { params }),
  createStructure: (data) => api.post("/fees/structure", null, { params: data }),
  updateStructure: (id, data) => api.put(`/fees/structure/${id}`, null, { params: data }),
  deleteStructure: (id) => api.delete(`/fees/structure/${id}`),
  createOrder: (feeStructureId, scholarship = 0, concession = 0) =>
    api.post("/fees/create-order", null, {
      params: { fee_structure_id: feeStructureId, scholarship_amount: scholarship, concession_amount: concession }
    }),
  verifyPayment: (data) => api.post("/fees/verify-payment", null, { params: data }),
  getPayments: (params) => api.get("/fees/payments", { params }),
  getPending: (params) => api.get("/fees/pending", { params }),
  initiateManualPayment: (feeStructureId) =>
    api.post(`/fees/initiate-manual-payment?fee_structure_id=${feeStructureId}`),
  uploadScreenshot: (paymentId, screenshotUrl, transactionId = "", bankRef = "") =>
    api.post(`/fees/upload-screenshot/${paymentId}`, null, {
      params: { screenshot_url: screenshotUrl, transaction_id: transactionId, bank_reference: bankRef }
    }),
  getPendingVerification: () => api.get("/fees/pending-verification"),
  verifyScreenshot: (paymentId, approved, remarks = "") =>
    api.put(`/fees/verify-screenshot/${paymentId}`, null, {
      params: { approved, remarks }
    }),
  getReceipt: (paymentId) => api.get(`/fees/receipt/${paymentId}`),
  sendReminders: () => api.post("/fees/send-reminders"),
  getNotificationHistory: (params) => api.get("/fees/notifications/history", { params }),
};

/* ---------------- MAIL ---------------- */
export const mailAPI = {
  send: (data) => api.post("/mail", data),
  getInbox: () => api.get("/mail/inbox"),
  getSent: () => api.get("/mail/sent"),
  getDrafts: () => api.get("/mail/drafts"),
  markRead: (mailId) => api.put(`/mail/${mailId}/read`),
  archive: (mailId) => api.put(`/mail/${mailId}/archive`),
  getRecipients: () => api.get("/mail/users"),
};

/* ---------------- DOCUMENTS ---------------- */
export const documentAPI = {
  create: (data) => api.post("/documents/request", data),
  getAll: (params) => api.get("/documents/requests", { params }),
  getOne: (requestId) => api.get(`/documents/requests/${requestId}`),
  verify: (requestId, remarks = "") =>
    api.put(`/documents/requests/${requestId}/verify`, null, { params: { remarks } }),
  forward: (requestId, remarks = "") =>
    api.put(`/documents/requests/${requestId}/forward`, null, { params: { remarks } }),
  approve: (requestId, remarks = "") =>
    api.put(`/documents/requests/${requestId}/approve`, null, { params: { remarks } }),
  sign: (requestId, remarks = "") =>
    api.put(`/documents/requests/${requestId}/sign`, null, { params: { remarks } }),
  issue: (requestId, remarks = "", file = null) => {
    if (file) {
      const formData = new FormData();
      if (remarks) formData.append("remarks", remarks);
      formData.append("file", file);
      return api.put(`/documents/requests/${requestId}/issue`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    }
    return api.put(`/documents/requests/${requestId}/issue`, null, { params: { remarks } });
  },
  reject: (requestId, remarks) =>
    api.put(`/documents/requests/${requestId}/reject`, null, { params: { remarks } }),
  download: (requestId) => api.get(`/documents/download/${requestId}`, { responseType: 'blob' }),
};

/* ---------------- ANNOUNCEMENTS ---------------- */
export const announcementAPI = {
  create: (data) => api.post("/announcements", data),
  getAll: () => api.get("/announcements"),
  update: (id, data) => api.put(`/announcements/${id}`, null, { params: data }),
  delete: (id) => api.delete(`/announcements/${id}`),
};

/* ---------------- GRIEVANCES ---------------- */
export const grievanceAPI = {
  submit: (data) => api.post("/grievances", data),
  getAll: (params) => api.get("/grievances", { params }),
  getOne: (grievanceId) => api.get(`/grievances/${grievanceId}`),
  getHODEscalated: () => api.get("/grievances/hod/escalated"),
  getHODPendingGrievances: () => api.get("/grievances/hod/pending"),
  getAllAdmin: (params) => api.get("/grievances/all", { params }),
  update: (id, data) => api.put(`/grievances/${id}`, data),
  delete: (id) => api.delete(`/grievances/${id}`),
  forward: (grievanceId, toLevel, remarks = "") =>
    api.put(`/grievances/${grievanceId}/forward`, null, {
      params: { to_level: toLevel, remarks },
    }),
  resolve: (grievanceId, resolution) =>
    api.put(`/grievances/${grievanceId}/resolve?resolution=${encodeURIComponent(resolution)}`),
  assign: (grievanceId, assignedTo) =>
    api.put(`/grievances/${grievanceId}/assign?assigned_to=${assignedTo}`),
  escalate: (grievanceId) => api.put(`/grievances/${grievanceId}/escalate`),
  addComment: (grievanceId, comment) =>
    api.post(`/grievances/${grievanceId}/comment?comment=${encodeURIComponent(comment)}`),
  getComments: (grievanceId) => api.get(`/grievances/${grievanceId}/comments`),
};

/* ---------------- ADMISSIONS ---------------- */
export const admissionAPI = {
  create: (data) => api.post("/admissions", data),
  getAll: (params) => api.get("/admissions", { params }),
  verify: (appId) => api.put(`/admissions/${appId}/verify`),
  hodApprove: (appId, approved, reason = "") =>
    api.put(`/admissions/${appId}/hod-approve?approved=${approved}&rejection_reason=${encodeURIComponent(reason)}`),
  principalApprove: (appId, approved, reason = "") =>
    api.put(`/admissions/${appId}/principal-approve?approved=${approved}&rejection_reason=${encodeURIComponent(reason)}`),
};

/* ---------------- LEAVE ---------------- */
export const leaveAPI = {
  submit: (data) => api.post("/leave-requests/apply", data),
  getAll: (params) => api.get("/leave-requests", { params }),
  getHODPending: () => api.get("/leave-requests/hod/pending"),
  approve: (requestId, approved) => api.put(`/leave-requests/${requestId}/approve?approved=${approved}`),
};

/* ---------------- AUDIT ---------------- */
export const auditAPI = {
  getAll: (params) => api.get("/audit-logs", { params }),
};

export const auditLogAPI = {
  getAll: (params) => api.get("/audit-logs", { params }),
  export: (params) => api.get("/audit-logs/export", { params, responseType: "blob" }),
};

/* ---------------- ANALYTICS ---------------- */
export const analyticsAPI = {
  getDashboard: () => api.get("/analytics/dashboard"),
  getFees: (params) => api.get("/analytics/fees", { params }),
  getAttendance: (params) => api.get("/analytics/attendance", { params }),
  getRisks: (params) => api.get("/analytics/risks", { params }),
  getStudentRisk: (studentId) => api.get(`/ai/risk-score/${studentId}`),
  getDepartmentRisks: (params) => api.get("/analytics/risks", { params }),
  getDepartmentAnalytics: (deptId) => api.get(`/departments/${deptId}/analytics`),
};

/* ---------------- SETTINGS ---------------- */
export const settingsAPI = {
  get: () => api.get("/settings"),
  update: (data) => api.put("/settings", data),
  changePassword: (data) => api.post("/change-password", data),
  getProfile: () => api.get("/profile"),
};

/* ---------------- UPLOAD ---------------- */
export const uploadAPI = {
  students: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/upload/students", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  marks: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/upload/marks", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  attendance: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/upload/attendance", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

/* ---------------- SEED ---------------- */
export const seedAPI = {
  seed: () => api.post("/seed"),
};

/* ---------------- ENHANCED STUDENTS ---------------- */
export const enhancedStudentAPI = {
  create: (formData) => api.post("/students/enhanced", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  }),
  updateProfile: (studentId, data) => api.put(`/students/${studentId}/profile`, null, { params: data }),
  getProfile: (studentId) => api.get(`/students/${studentId}/full-profile`),
  getFullProfile: (studentId) => api.get(`/students/${studentId}/full-profile`),
  uploadDocument: (studentId, documentType, file) => {
    const formData = new FormData();
    formData.append("document_type", documentType);
    formData.append("file", file);
    return api.post(`/upload/document/${studentId}`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  getDocuments: (studentId) => api.get(`/students/${studentId}/documents`),
};

/* ---------------- NOTIFICATIONS ---------------- */
export const notificationAPI = {
  getMy: (unreadOnly = false) => api.get("/notifications/my", { params: { unread_only: unreadOnly } }),
  markRead: (notificationId) => api.put(`/notifications/${notificationId}/read`),
  markAllRead: () => api.put("/notifications/mark-all-read"),
  create: (data) => api.post("/notifications", data),
  delete: (id) => api.delete(`/notifications/${id}`),
};

/* ---------------- CHATBOT ---------------- */
export const chatbotAPI = {
  sendMessage: (message, sessionId = null) => api.post("/chatbot/message", null, {
    params: { message, session_id: sessionId }
  }),
  getSessions: () => api.get("/chatbot/sessions"),
  deleteSession: (sessionId) => api.delete(`/chatbot/session/${sessionId}`),
};

/* ---------------- TIMETABLE ---------------- */
export const timetableAPI = {
  getToday: (date = null) => api.get("/timetable/today", { params: { date } }),
  createManualEntry: (data) => api.post("/timetable/manual", null, { params: data }),
  updateEntry: (entryId, data) => api.put(`/timetable/manual/${entryId}`, null, { params: data }),
  deleteEntry: (entryId) => api.delete(`/timetable/manual/${entryId}`),
};

/* ---------------- PREFERENCES ---------------- */
export const preferencesAPI = {
  get: () => api.get("/preferences"),
  update: (data) => api.put("/preferences", null, { params: data }),
};

/* ---------------- FEES ANALYTICS ---------------- */
export const feesAnalyticsAPI = {
  getAnalytics: (academicYear = null, departmentId = null) =>
    api.get("/analytics/fees", { params: { academic_year: academicYear, department_id: departmentId } }),
};

/* ---------------- COMMUNICATIONS ---------------- */
export const communicationAPI = {
  send: (data) => api.post("/communications/send", data),
  getInbox: (params) => api.get("/communications/inbox", { params }),
  getSent: (params) => api.get("/communications/sent", { params }),
  getOne: (id) => api.get(`/communications/${id}`),
  delete: (id) => api.delete(`/communications/${id}`)
};