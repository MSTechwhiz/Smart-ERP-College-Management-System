import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  ClipboardCheck,
  FileSpreadsheet,
  CreditCard,
  Megaphone,
  FileText,
  MessageSquare,
  Calendar,
  Settings,
  TrendingUp,
  Download,
  Calculator,
  Pencil,
  Trash2,
  Users,
  Clock
} from 'lucide-react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Progress } from '../../components/ui/progress';
import { Textarea } from '../../components/ui/textarea';
import { Label } from '../../components/ui/label';
import { Input } from '../../components/ui/input';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../../components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/select';
import { CGPACalculator } from '../../components/ui/CGPACalculator';
import {
  studentAPI,
  attendanceAPI,
  marksAPI,
  feeAPI,
  announcementAPI,
  documentAPI,
  grievanceAPI,
  leaveAPI,
  subjectAPI
} from '../../services/api';
import { toast } from 'sonner';
import { useAuth } from '../../context/AuthContext';
import { formatCurrency, formatDateTime, getGradeColor, getStatusColor, getYearLabel } from '../../lib/utils';
import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { Communications } from '../shared/Communications';

const sidebarItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/student' },
  { icon: ClipboardCheck, label: 'Attendance', href: '/student/attendance' },
  { icon: Clock, label: 'Timetable', href: '/student/timetable' },
  { icon: FileSpreadsheet, label: 'Marks', href: '/student/marks' },
  { icon: TrendingUp, label: 'CGPA', href: '/student/cgpa' },
  { icon: Calculator, label: 'CGPA Calculator', href: '/student/cgpa-calculator' },
  { icon: CreditCard, label: 'Fees', href: '/student/fees' },
  { icon: FileText, label: 'Documents', href: '/student/documents' },
  { icon: MessageSquare, label: 'Grievances', href: '/student/grievances' },
  { icon: Calendar, label: 'Apply Leave', href: '/student/leave' },
  { icon: Megaphone, label: 'Announcements', href: '/student/announcements' },
  { icon: MessageSquare, label: 'Communications', href: '/student/communications' },
  { icon: Settings, label: 'Settings', href: '/student/settings' },
];

// Dashboard Overview
function DashboardOverview() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [attendanceSummary, setAttendanceSummary] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [profileRes, announcementsRes] = await Promise.all([
        studentAPI.getMyProfile(),
        announcementAPI.getAll()
      ]);
      setProfile(profileRes.data);
      setAnnouncements(announcementsRes.data.slice(0, 3));

      // Load attendance summary
      if (profileRes.data?.id) {
        const attendanceRes = await attendanceAPI.getSummary(profileRes.data.id);
        setAttendanceSummary(attendanceRes.data.summary || []);
      }
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  // Calculate overall attendance
  const overallAttendance = attendanceSummary.length > 0
    ? attendanceSummary.reduce((acc, s) => acc + s.percentage, 0) / attendanceSummary.length
    : 0;

  const attendanceData = [
    { name: 'Attendance', value: overallAttendance, fill: overallAttendance >= 75 ? '#10b981' : '#ef4444' }
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <Card
        className="border-0 overflow-hidden"
        style={{
          background: `linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.9)), url('https://images.unsplash.com/photo-1744320911030-1ab998d994d7?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2OTF8MHwxfHNlYXJjaHw0fHxjb2xsZWdlJTIwc3R1ZGVudHMlMjBkaXZlcnNlJTIwc3R1ZHlpbmclMjBncm91cCUyMGhhcHB5fGVufDB8fHx8MTc3MDUyNDA4M3ww&ixlib=rb-4.1.0&q=85')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <CardContent className="pt-6 pb-8 text-white">
          <h2 className="text-2xl font-bold mb-2">Welcome back, {profile?.name}</h2>
          <div className="flex flex-wrap items-center gap-4 text-sm opacity-90">
            <span className="mono">Roll No: {profile?.roll_number}</span>
            <span>•</span>
            <span>{profile?.department_name}</span>
            <span>•</span>
            <span>{getYearLabel(profile?.semester)} (Sem {profile?.semester})</span>
            <span>•</span>
            <span>Batch {profile?.batch}</span>
          </div>
        </CardContent>
      </Card>

      {/* Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* CGPA Card */}
        <Card className="stat-card">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Current CGPA</p>
                <p className="text-4xl font-bold mono text-emerald-600">
                  {(!profile?.cgpa || profile?.cgpa === 0) ? 'N/A' : profile?.cgpa.toFixed(2)}
                </p>
              </div>
              <div className="h-16 w-16 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                <TrendingUp className="h-8 w-8 text-emerald-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Attendance Card */}
        <Card className="stat-card">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Overall Attendance</p>
                <p className={`text-4xl font-bold mono ${overallAttendance >= 75 ? 'text-emerald-600' : 'text-rose-600'}`}>
                  {overallAttendance.toFixed(1)}%
                </p>
              </div>
              <div className="h-16 w-16">
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="100%" data={attendanceData} startAngle={90} endAngle={-270}>
                    <RadialBar dataKey="value" cornerRadius={10} background />
                  </RadialBarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Semester Card */}
        <Card className="stat-card">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Current Status</p>
                <p className="text-2xl font-bold mono text-blue-600">
                  {getYearLabel(profile?.semester)}
                </p>
                <p className="text-xs text-muted-foreground">Sem {profile?.semester || 1}</p>
              </div>
              <div className="h-16 w-16 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                <Calendar className="h-8 w-8 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions & Announcements */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-3">
            <Button variant="outline" className="h-auto py-4 flex-col gap-2" data-testid="view-marks-btn" onClick={() => navigate('/student/marks')}>
              <FileSpreadsheet className="h-5 w-5" />
              <span>View Marks</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col gap-2" data-testid="pay-fees-btn" onClick={() => navigate('/student/fees')}>
              <CreditCard className="h-5 w-5" />
              <span>Pay Fees</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col gap-2" data-testid="request-document-btn" onClick={() => navigate('/student/documents')}>
              <FileText className="h-5 w-5" />
              <span>Request Document</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col gap-2" data-testid="submit-grievance-btn" onClick={() => navigate('/student/grievances')}>
              <MessageSquare className="h-5 w-5" />
              <span>Submit Grievance</span>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Megaphone className="h-5 w-5 text-amber-600" />
              Announcements
            </CardTitle>
          </CardHeader>
          <CardContent>
            {announcements.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">No announcements</p>
            ) : (
              <div className="space-y-4">
                {announcements.map((ann) => (
                  <div key={ann.id} className="p-3 rounded-lg bg-muted/50">
                    <h4 className="font-medium text-sm">{ann.title}</h4>
                    <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{ann.content}</p>
                    <p className="text-xs text-muted-foreground mt-2">
                      {formatDateTime(ann.publish_date)}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Attendance Page
function AttendancePage() {
  const [summary, setSummary] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAttendance();
  }, []);

  const loadAttendance = async () => {
    try {
      const profileRes = await studentAPI.getMyProfile();
      if (profileRes.data?.id) {
        const response = await attendanceAPI.getSummary(profileRes.data.id);
        setSummary(response.data.summary || []);
      }
    } catch (error) {
      toast.error('Failed to load attendance');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Attendance Summary</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {summary.length === 0 ? (
          <Card className="col-span-full">
            <CardContent className="py-8 text-center text-muted-foreground">
              No attendance records found
            </CardContent>
          </Card>
        ) : (
          summary.map((subj, idx) => (
            <Card key={idx}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="font-semibold">{subj.subject_name}</h3>
                    <p className="text-sm text-muted-foreground mono">{subj.subject_code}</p>
                  </div>
                  <Badge className={subj.percentage >= 75 ? 'badge-success' : 'badge-error'}>
                    {subj.percentage.toFixed(1)}%
                  </Badge>
                </div>
                <Progress value={subj.percentage} className="h-2 mb-3" />
                <div className="flex justify-between text-sm text-muted-foreground">
                  <span>Present: {subj.present}</span>
                  <span>Absent: {subj.absent}</span>
                  <span>OD: {subj.od}</span>
                  <span>Total: {subj.total}</span>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

// Marks Page
function MarksPage() {
  const [marks, setMarks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMarks();
  }, []);

  const loadMarks = async () => {
    try {
      const response = await marksAPI.getAll();
      setMarks(response.data);
    } catch (error) {
      toast.error('Failed to load marks');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">My Marks</h2>

      <Card>
        <CardContent className="pt-6">
          {marks.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No marks found</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium">Subject</th>
                    <th className="text-center py-3 px-2 font-medium">CIA1</th>
                    <th className="text-center py-3 px-2 font-medium">CIA2</th>
                    <th className="text-center py-3 px-2 font-medium">CIA3</th>
                    <th className="text-center py-3 px-2 font-medium">CIA4</th>
                    <th className="text-center py-3 px-2 font-medium">Model</th>
                    <th className="text-center py-3 px-2 font-medium">Total</th>
                    <th className="text-center py-3 px-2 font-medium">Grade</th>
                  </tr>
                </thead>
                <tbody>
                  {marks.map((mark) => (
                    <tr key={mark.id} className="border-b hover:bg-muted/50">
                      <td className="py-3 px-4">
                        <p className="font-medium">{mark.subject_name}</p>
                        <p className="text-xs text-muted-foreground mono">{mark.subject_code}</p>
                      </td>
                      <td className="text-center py-3 px-2 mono">{mark.cia1 ?? '-'}</td>
                      <td className="text-center py-3 px-2 mono">{mark.cia2 ?? '-'}</td>
                      <td className="text-center py-3 px-2 mono">{mark.cia3 ?? '-'}</td>
                      <td className="text-center py-3 px-2 mono">{mark.cia4 ?? '-'}</td>
                      <td className="text-center py-3 px-2 mono">{mark.model_exam ?? '-'}</td>
                      <td className="text-center py-3 px-2 mono font-medium">{mark.total?.toFixed(1) ?? '-'}</td>
                      <td className="text-center py-3 px-2">
                        {mark.grade ? (
                          <Badge className={getGradeColor(mark.grade)}>{mark.grade}</Badge>
                        ) : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// CGPA Page
function CGPAPage() {
  const [cgpaData, setCgpaData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCGPA();
  }, []);

  const loadCGPA = async () => {
    try {
      const profileRes = await studentAPI.getMyProfile();
      if (profileRes.data?.id) {
        const response = await marksAPI.getCGPA(profileRes.data.id);
        setCgpaData(response.data);
      }
    } catch (error) {
      toast.error('Failed to load CGPA');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">CGPA Summary</h2>

      <Card className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white border-0">
        <CardContent className="pt-6 pb-8 text-center">
          <p className="text-sm opacity-90 mb-2">Cumulative GPA</p>
          <p className="text-6xl font-bold mono">{cgpaData?.cgpa?.toFixed(2) || '0.00'}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Semester-wise GPA</CardTitle>
        </CardHeader>
        <CardContent>
          {cgpaData?.semester_gpa?.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No semester data available</p>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {cgpaData?.semester_gpa?.map((sem) => (
                <div key={sem.semester} className="p-4 rounded-xl bg-muted/50 text-center">
                  <p className="text-sm text-muted-foreground">Semester {sem.semester}</p>
                  <p className="text-2xl font-bold mono mt-1">{sem.gpa.toFixed(2)}</p>
                  <p className="text-xs text-muted-foreground mt-1">{sem.credits} credits</p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Fees Page with QR Code Payment Flow
function FeesPage() {
  const [pending, setPending] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [paymentDialog, setPaymentDialog] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [screenshotUrl, setScreenshotUrl] = useState('');
  const [transactionId, setTransactionId] = useState('');

  useEffect(() => {
    loadFees();
  }, []);

  const loadFees = async () => {
    try {
      const [pendingRes, paymentsRes] = await Promise.all([
        feeAPI.getPending(),
        feeAPI.getPayments()
      ]);
      setPending(pendingRes.data);
      setPayments(paymentsRes.data);
    } catch (error) {
      toast.error('Failed to load fees');
    } finally {
      setLoading(false);
    }
  };

  const handlePayNow = async (fee) => {
    try {
      const response = await feeAPI.initiateManualPayment(fee.id);
      setPaymentDialog({
        ...response.data,
        fee: fee
      });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to initiate payment');
    }
  };

  const handleUploadScreenshot = async () => {
    if (!screenshotUrl.trim()) {
      toast.error('Please enter screenshot URL');
      return;
    }

    setUploading(true);
    try {
      await feeAPI.uploadScreenshot(paymentDialog.payment.id, screenshotUrl, transactionId);
      toast.success('Screenshot uploaded! Awaiting verification.');
      setPaymentDialog(null);
      setScreenshotUrl('');
      setTransactionId('');
      loadFees();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload screenshot');
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Fee Management</h2>

      {/* Payment Dialog with QR Code */}
      <Dialog open={!!paymentDialog} onOpenChange={() => { setPaymentDialog(null); setScreenshotUrl(''); setTransactionId(''); }}>
        <DialogContent className="max-w-lg" aria-describedby={undefined}>
          <DialogHeader>
            <DialogTitle>Pay Fee - {paymentDialog?.fee?.name}</DialogTitle>
            <CardDescription>
              Amount: <span className="font-bold text-primary">{formatCurrency(paymentDialog?.fee?.amount || 0)}</span>
            </CardDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Bank Details */}
            <div className="p-4 rounded-lg bg-muted/50">
              <h4 className="font-medium mb-3">Bank Transfer Details</h4>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <span className="text-muted-foreground">Account Name:</span>
                <span className="font-medium">{paymentDialog?.bank_details?.account_name}</span>
                <span className="text-muted-foreground">Account Number:</span>
                <span className="font-medium mono">{paymentDialog?.bank_details?.account_number}</span>
                <span className="text-muted-foreground">IFSC Code:</span>
                <span className="font-medium mono">{paymentDialog?.bank_details?.ifsc_code}</span>
                <span className="text-muted-foreground">Bank:</span>
                <span className="font-medium">{paymentDialog?.bank_details?.bank_name}</span>
              </div>
            </div>

            {/* UPI Details */}
            <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-950/30 text-center">
              <h4 className="font-medium mb-2">Or Pay via UPI</h4>
              <p className="text-lg mono font-bold text-blue-600">{paymentDialog?.upi_id}</p>
              <div className="mt-4 p-4 bg-white dark:bg-slate-900 rounded-lg inline-block">
                <div className="w-32 h-32 bg-gray-200 dark:bg-gray-700 rounded flex items-center justify-center">
                  <span className="text-xs text-muted-foreground">QR Code</span>
                </div>
              </div>
              <p className="text-xs text-muted-foreground mt-2">Scan QR to pay</p>
            </div>

            {/* Screenshot Upload */}
            <div className="space-y-4 border-t pt-4">
              <h4 className="font-medium">Upload Payment Screenshot</h4>
              <div className="space-y-2">
                <Label>Screenshot URL / Image Link</Label>
                <Input
                  data-testid="screenshot-url-input"
                  value={screenshotUrl}
                  onChange={(e) => setScreenshotUrl(e.target.value)}
                  placeholder="Paste image URL or upload to cloud storage"
                />
              </div>
              <div className="space-y-2">
                <Label>Transaction ID (Optional)</Label>
                <Input
                  data-testid="transaction-id-input"
                  value={transactionId}
                  onChange={(e) => setTransactionId(e.target.value)}
                  placeholder="UTR / Transaction Reference Number"
                />
              </div>
              <Button
                onClick={handleUploadScreenshot}
                className="w-full"
                disabled={uploading}
                data-testid="submit-screenshot-btn"
              >
                {uploading ? 'Uploading...' : 'Submit for Verification'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pending Fees */}
        <Card>
          <CardHeader>
            <CardTitle className="text-amber-600">Pending Fees</CardTitle>
          </CardHeader>
          <CardContent>
            {pending.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">No pending fees</p>
            ) : (
              <div className="space-y-3">
                {pending.map((fee) => (
                  <div key={fee.id} className="flex items-center justify-between p-4 rounded-lg border">
                    <div>
                      <p className="font-medium">{fee.name}</p>
                      <p className="text-sm text-muted-foreground capitalize">{fee.category}</p>
                      {fee.due_date && (
                        <p className="text-xs text-red-500 mt-1">Due: {fee.due_date}</p>
                      )}
                    </div>
                    <div className="text-right">
                      <p className="font-bold mono">{formatCurrency(fee.amount)}</p>
                      <Button
                        size="sm"
                        className="mt-2"
                        onClick={() => handlePayNow(fee)}
                        data-testid={`pay-fee-${fee.id}`}
                      >
                        Pay Now
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Payment History */}
        <Card>
          <CardHeader>
            <CardTitle>Payment History</CardTitle>
          </CardHeader>
          <CardContent>
            {payments.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">No payment history</p>
            ) : (
              <div className="space-y-3">
                {payments.map((payment) => (
                  <div key={payment.id} className="flex items-center justify-between p-4 rounded-lg border">
                    <div>
                      <p className="font-medium">{payment.fee_name}</p>
                      <p className="text-xs text-muted-foreground">
                        {formatDateTime(payment.payment_date)}
                      </p>
                      {payment.receipt_number && (
                        <p className="text-xs mono text-green-600">Receipt: {payment.receipt_number}</p>
                      )}
                    </div>
                    <div className="text-right">
                      <p className="font-bold mono">{formatCurrency(payment.amount)}</p>
                      <Badge className={getStatusColor(payment.status)}>
                        {payment.status.replace('_', ' ')}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Documents Page
function DocumentsPage() {
  const [requests, setRequests] = useState([]);
  const [docType, setDocType] = useState('');
  const [customDocType, setCustomDocType] = useState('');
  const [deliveryType, setDeliveryType] = useState('hard');
  const [remarks, setRemarks] = useState('');
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [detailDialog, setDetailDialog] = useState(null);

  useEffect(() => {
    loadRequests();
  }, []);

  const loadRequests = async () => {
    try {
      const response = await documentAPI.getAll();
      setRequests(response.data);
    } catch (error) {
      console.error('Error loading requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    const finalDocType = docType === 'other' ? customDocType : docType;
    if (!finalDocType) {
      toast.error('Please select or enter document type');
      return;
    }

    setSubmitting(true);
    try {
      await documentAPI.create({
        document_type: finalDocType,
        remarks: remarks,
        delivery_type: deliveryType
      });
      toast.success('Document request submitted');
      setDocType('');
      setCustomDocType('');
      setDeliveryType('hard');
      setRemarks('');
      loadRequests();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit request');
    } finally {
      setSubmitting(false);
    }
  };
  const handleDownload = async (req, e) => {
    e.stopPropagation();
    setDownloading(req.id);
    try {
      const response = await documentAPI.download(req.id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${req.document_type.replace('_', ' ')}_${req.roll_number || req.id.slice(-6)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Download started');
    } catch (error) {
      toast.error('Failed to download document');
    } finally {
      setDownloading(null);
    }
  };

  const getStatusSteps = (status) => {
    const steps = ['Pending', 'Verified', 'Approved', 'Signed', 'Issued'];
    const currentIndex = steps.indexOf(status);
    return steps.map((step, index) => ({
      step,
      completed: index <= currentIndex && status !== 'rejected',
      current: step === status
    }));
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Document Requests</h2>

      {/* Detail Dialog */}
      <Dialog open={!!detailDialog} onOpenChange={() => setDetailDialog(null)}>
        <DialogContent className="max-w-lg" aria-describedby={undefined}>
          <DialogHeader>
            <DialogTitle className="capitalize">{detailDialog?.document_type?.replace('_', ' ')} Request</DialogTitle>
            <CardDescription>Ticket: {detailDialog?.ticket_id || detailDialog?.id?.slice(-8)}</CardDescription>
          </DialogHeader>
          <div className="space-y-4">
            {/* Status Timeline */}
            <div className="p-4 rounded-lg bg-muted/50">
              <h4 className="font-medium mb-3">Request Status</h4>
              <div className="flex justify-between">
                {getStatusSteps(detailDialog?.status).map((s, i) => (
                  <div key={s.step} className="flex flex-col items-center text-xs">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${s.completed ? 'bg-green-500 text-white' :
                      s.current ? 'bg-blue-500 text-white' :
                        'bg-gray-200 dark:bg-gray-700'
                      }`}>
                      {i + 1}
                    </div>
                    <span className="mt-1 capitalize">{s.step}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* History */}
            {detailDialog?.history?.length > 0 && (
              <div>
                <h4 className="font-medium mb-2">History</h4>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {detailDialog.history.map((h, i) => (
                    <div key={i} className="text-sm p-2 rounded bg-muted/30">
                      <p className="font-medium">{h.action}</p>
                      <p className="text-muted-foreground text-xs">{h.timestamp} by {h.by}</p>
                      {h.remarks && <p className="text-xs mt-1">"{h.remarks}"</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {detailDialog?.status === 'rejected' && (
              <div className="p-3 bg-red-50 dark:bg-red-950/30 rounded text-sm text-red-600">
                <strong>Rejection Reason:</strong> {detailDialog?.rejection_reason || 'No reason provided'}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Request Form */}
        <Card>
          <CardHeader>
            <CardTitle>New Request</CardTitle>
            <CardDescription>Request official documents</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Document Type</Label>
              <Select value={docType} onValueChange={setDocType}>
                <SelectTrigger data-testid="doc-type-select">
                  <SelectValue placeholder="Select document type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="bonafide">Bonafide Certificate</SelectItem>
                  <SelectItem value="tc">Transfer Certificate</SelectItem>
                  <SelectItem value="marksheet">Marksheet Copy</SelectItem>
                  <SelectItem value="fee_letter">Fee Letter</SelectItem>
                  <SelectItem value="character_certificate">Character Certificate</SelectItem>
                  <SelectItem value="medium_certificate">Medium of Instruction</SelectItem>
                  <SelectItem value="other">Other (Custom)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {docType === 'other' && (
              <div className="space-y-2">
                <Label>Specify Document Type</Label>
                <Input
                  data-testid="custom-doc-type-input"
                  value={customDocType}
                  onChange={(e) => setCustomDocType(e.target.value)}
                  placeholder="Enter document name"
                />
              </div>
            )}
            <div className="space-y-2">
              <Label>Delivery Type</Label>
              <Select value={deliveryType} onValueChange={setDeliveryType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hard">Hard Copy (Collect from Office)</SelectItem>
                  <SelectItem value="soft">Soft Copy (Direct Download)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Additional Remarks (Optional)</Label>
              <Textarea
                data-testid="doc-remarks-input"
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                placeholder="Any specific requirements or purpose"
                rows={2}
              />
            </div>
            <Button
              className="w-full"
              onClick={handleSubmit}
              disabled={submitting}
              data-testid="submit-doc-request-btn"
            >
              {submitting ? 'Submitting...' : 'Submit Request'}
            </Button>
          </CardContent>
        </Card>

        {/* Request Status */}
        <Card>
          <CardHeader>
            <CardTitle>Request Status</CardTitle>
          </CardHeader>
          <CardContent>
            {requests.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">No requests found</p>
            ) : (
              <div className="space-y-3">
                {requests.map((req) => (
                  <div
                    key={req.id}
                    className="flex items-center justify-between p-4 rounded-lg border cursor-pointer hover:bg-muted/30 transition-colors"
                    onClick={() => setDetailDialog(req)}
                    data-testid={`doc-request-${req.id}`}
                  >
                    <div>
                      <p className="font-medium capitalize">{req.document_type.replace('_', ' ')}</p>
                      <p className="text-xs text-muted-foreground">
                        {formatDateTime(req.submitted_at)}
                      </p>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <Badge className={getStatusColor(req.status)}>
                        {req.status.replace('_', ' ')}
                      </Badge>
                      {req.delivery_type === 'soft' && req.status.toLowerCase() === 'issued' && (
                        <Button 
                          size="sm" 
                          variant="ghost" 
                          className="h-8 text-primary hover:text-primary hover:bg-primary/10 gap-1"
                          onClick={(e) => handleDownload(req, e)}
                          disabled={downloading === req.id}
                        >
                          <Download className={`h-4 w-4 ${downloading === req.id ? 'animate-bounce' : ''}`} />
                          {downloading === req.id ? 'Downloading...' : 'Download'}
                        </Button>
                      )}
                      <p className="text-[10px] text-muted-foreground uppercase">
                        {req.delivery_type === 'soft' ? 'Soft Copy' : 'Hard Copy'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function ApplyLeavePage() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    leave_type: 'Personal Leave',
    from_date: '',
    to_date: '',
    reason: '',
    attachment_url: ''
  });

  useEffect(() => {
    loadRequests();
  }, []);

  const loadRequests = async () => {
    try {
      const response = await leaveAPI.getAll();
      setRequests(response.data);
    } catch (error) {
      console.error('Error loading leave requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.from_date || !formData.to_date || !formData.reason) {
      toast.error('Please fill all required fields');
      return;
    }

    setSubmitting(true);
    try {
      await leaveAPI.submit(formData);
      toast.success('Leave request submitted successfully');
      setFormData({
        leave_type: 'Personal Leave',
        from_date: '',
        to_date: '',
        reason: '',
        attachment_url: ''
      });
      loadRequests();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit leave request');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Apply Leave</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <Card>
          <CardHeader>
            <CardTitle>New Leave Request</CardTitle>
            <CardDescription>Submit your leave application for HOD approval</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label>Leave Type</Label>
                <Select
                  value={formData.leave_type}
                  onValueChange={(value) => setFormData({ ...formData, leave_type: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select leave type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Medical Leave">Medical Leave</SelectItem>
                    <SelectItem value="Personal Leave">Personal Leave</SelectItem>
                    <SelectItem value="Emergency Leave">Emergency Leave</SelectItem>
                    <SelectItem value="Other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>From Date</Label>
                  <Input
                    type="date"
                    value={formData.from_date}
                    onChange={(e) => setFormData({ ...formData, from_date: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label>To Date</Label>
                  <Input
                    type="date"
                    value={formData.to_date}
                    onChange={(e) => setFormData({ ...formData, to_date: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Reason</Label>
                <Textarea
                  value={formData.reason}
                  onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                  placeholder="Explain the reason for leave..."
                  rows={4}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label>Attachment URL (Optional)</Label>
                <Input
                  type="url"
                  value={formData.attachment_url}
                  onChange={(e) => setFormData({ ...formData, attachment_url: e.target.value })}
                  placeholder="Link to supporting document (e.g. medical certificate)"
                />
              </div>

              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting ? 'Submitting...' : 'Submit Leave Request'}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* History */}
        <Card>
          <CardHeader>
            <CardTitle>My Leave Requests</CardTitle>
            <CardDescription>Track the status of your applications</CardDescription>
          </CardHeader>
          <CardContent>
            {requests.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">No leave requests found</p>
            ) : (
              <div className="space-y-4">
                {requests.map((req) => (
                  <div key={req.id} className="p-4 rounded-lg border space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold">{req.leave_type}</span>
                      <Badge className={getStatusColor(req.status)}>
                        {req.status}
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      <p>{req.from_date} to {req.to_date}</p>
                      <p className="mt-1 line-clamp-2 italic">"{req.reason}"</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Grievances Page with Timeline
function GrievancesPage() {
  const [grievances, setGrievances] = useState([]);
  const [formData, setFormData] = useState({ subject: '', description: '', category: 'academic', target_type: 'faculty' });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [detailDialog, setDetailDialog] = useState(null);
  const [editingId, setEditingId] = useState(null);

  useEffect(() => {
    loadGrievances();
  }, []);

  const loadGrievances = async () => {
    try {
      const response = await grievanceAPI.getAll();
      setGrievances(response.data);
    } catch (error) {
      console.error('Error loading grievances:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!formData.subject || !formData.description) {
      toast.error('Please fill all fields');
      return;
    }

    setSubmitting(true);
    try {
      if (editingId) {
        await grievanceAPI.update(editingId, formData);
        toast.success('Grievance updated successfully');
      } else {
        await grievanceAPI.submit(formData);
        toast.success('Grievance submitted successfully');
      }
      setFormData({ subject: '', description: '', category: 'academic' });
      setEditingId(null);
      loadGrievances();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (g) => {
    setFormData({
      subject: g.subject,
      description: g.description,
      category: g.category
    });
    setEditingId(g.id);
  };

  const handleCancelEdit = () => {
    setFormData({ subject: '', description: '', category: 'academic' });
    setEditingId(null);
  };

  const getGrievanceSteps = (status, currentLevel, targetType) => {
    const levels = targetType === 'faculty' ? ['faculty', 'hod'] : ['admin', 'principal'];
    const levelIndex = levels.indexOf(currentLevel);

    const steps = [];
    steps.push({ step: 'Submitted', completed: true });

    if (targetType === 'faculty') {
      steps.push({ step: 'At Faculty', current: currentLevel === 'faculty' && status !== 'resolved', completed: levelIndex > 0 || status === 'resolved' });
      steps.push({ step: 'At HOD', current: currentLevel === 'hod' && status !== 'resolved', completed: status === 'resolved' && levelIndex >= 1 });
    } else {
      steps.push({ step: 'At Admin', current: currentLevel === 'admin' && status !== 'resolved', completed: levelIndex > 0 || status === 'resolved' });
      steps.push({ step: 'At Principal', current: currentLevel === 'principal' && status !== 'resolved', completed: status === 'resolved' && levelIndex >= 1 });
    }

    steps.push({ step: 'Resolved', current: status === 'resolved', completed: status === 'resolved' });

    return steps;
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Grievances</h2>

      {/* Detail Dialog */}
      <Dialog open={!!detailDialog} onOpenChange={() => setDetailDialog(null)}>
        <DialogContent className="max-w-lg" aria-describedby={undefined}>
          <DialogHeader>
            <DialogTitle>{detailDialog?.subject}</DialogTitle>
            <CardDescription>Ticket ID: {detailDialog?.ticket_id || detailDialog?.id?.slice(-8)}</CardDescription>
          </DialogHeader>
          <div className="space-y-4">
            {/* Status */}
            <div className="flex items-center gap-2">
              <Badge className={getStatusColor(detailDialog?.status)}>
                {detailDialog?.status?.replace('_', ' ')}
              </Badge>
              <span className="text-sm text-muted-foreground capitalize">
                Category: {detailDialog?.category}
              </span>
            </div>

            {/* Description */}
            <div className="p-3 rounded bg-muted/50">
              <p className="text-sm">{detailDialog?.description}</p>
            </div>

            {/* Status Timeline */}
            <div className="p-4 rounded-lg border">
              <h4 className="font-medium mb-3">Status Timeline</h4>
              <div className="flex justify-between">
                {getGrievanceSteps(detailDialog?.status, detailDialog?.current_level, detailDialog?.target_type).map((s, i) => (
                  <div key={s.step} className="flex flex-col items-center text-xs">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${s.completed ? 'bg-green-500 text-white' :
                      s.current ? 'bg-blue-500 text-white' :
                        'bg-gray-200 dark:bg-gray-700'
                      }`}>
                      {i + 1}
                    </div>
                    <span className="mt-1 text-center whitespace-nowrap">{s.step}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* History/Comments */}
            {detailDialog?.history?.length > 0 && (
              <div>
                <h4 className="font-medium mb-2">Activity Log</h4>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {detailDialog.history.map((h, i) => (
                    <div key={i} className="text-sm p-2 rounded bg-muted/30">
                      <div className="flex justify-between">
                        <span className="font-medium">{h.action}</span>
                        <span className="text-xs text-muted-foreground">{h.timestamp}</span>
                      </div>
                      <p className="text-xs text-muted-foreground">by {h.by}</p>
                      {h.remarks && <p className="text-xs mt-1 italic">"{h.remarks}"</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Resolution */}
            {detailDialog?.resolution && (
              <div className="p-3 bg-green-50 dark:bg-green-950/30 rounded">
                <h4 className="font-medium text-green-700 dark:text-green-400 text-sm">Resolution</h4>
                <p className="text-sm mt-1">{detailDialog.resolution}</p>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>{editingId ? 'Update Grievance' : 'Submit Grievance'}</CardTitle>
            <CardDescription>
              {formData.target_type === 'faculty'
                ? 'Academic path: Faculty → HOD → Resolution'
                : 'Administrative path: Admin → Principal → Resolution'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Category</Label>
                <Select
                  value={formData.category}
                  onValueChange={(value) => setFormData({ ...formData, category: value })}
                >
                  <SelectTrigger data-testid="grievance-category-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="academic">Academic</SelectItem>
                    <SelectItem value="fee">Fee Related</SelectItem>
                    <SelectItem value="hostel">Hostel</SelectItem>
                    <SelectItem value="infrastructure">Infrastructure</SelectItem>
                    <SelectItem value="faculty">Faculty Related</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Send To</Label>
                <Select
                  value={formData.target_type}
                  onValueChange={(value) => setFormData({ ...formData, target_type: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="faculty">Faculty (Academic)</SelectItem>
                    <SelectItem value="admin">Admin (Administrative)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label>Subject</Label>
              <Input
                data-testid="grievance-subject-input"
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                placeholder="Brief subject of your grievance"
              />
            </div>
            <div className="space-y-2">
              <Label>Description</Label>
              <Textarea
                data-testid="grievance-description-input"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Detailed description of your grievance"
                rows={4}
              />
            </div>
            <div className="flex gap-2">
              <Button
                className="flex-1"
                onClick={handleSubmit}
                disabled={submitting}
                data-testid="submit-grievance-btn"
              >
                {submitting ? 'Processing...' : (editingId ? 'Update Grievance' : 'Submit Grievance')}
              </Button>
              {editingId && (
                <Button variant="outline" onClick={handleCancelEdit}>
                  Cancel
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>My Grievances</CardTitle>
          </CardHeader>
          <CardContent>
            {grievances.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">No grievances submitted</p>
            ) : (
              <div className="space-y-3">
                {grievances.map((g) => (
                  <div
                    key={g.id}
                    className={`p-4 rounded-lg border cursor-pointer hover:bg-muted/30 transition-colors ${editingId === g.id ? 'ring-2 ring-primary' : ''}`}
                    onClick={() => setDetailDialog(g)}
                    data-testid={`grievance-${g.id}`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium">{g.subject}</h4>
                          {['open', 'pending'].includes(g.status) && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-6 w-6"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleEdit(g);
                              }}
                              title="Edit Grievance"
                            >
                              <Pencil className="h-3 w-3" />
                            </Button>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground capitalize">{g.category}</p>
                      </div>
                      <Badge className={getStatusColor(g.status)}>{g.status.replace('_', ' ')}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2">{g.description}</p>
                    {g.current_level && g.status !== 'resolved' && (
                      <p className="text-xs mt-2 text-blue-600">Currently at: {g.current_level.toUpperCase()}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Announcements Page
import AnnouncementsPage from '../common/AnnouncementsPage';

// Profile/Settings Page - Use Shared Component
import { SettingsPage as SharedSettingsPage, ProfilePage as SharedProfilePage } from '../../components/ui/SettingsPage';

function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await studentAPI.getMyProfile();
      setProfile(response.data);
    } catch (error) {
      toast.error('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <SharedProfilePage profile={profile} loading={loading} />
    </div>
  );
}

// Settings Page with Profile
function SettingsPageWrapper() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await studentAPI.getMyProfile();
      setProfile(response.data);
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <SharedSettingsPage />

      {/* Student Profile Details */}
      <Card>
        <CardHeader>
          <CardTitle>Student Profile</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-20">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
            </div>
          ) : profile && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label className="text-muted-foreground">Full Name</Label>
                <p className="font-medium text-lg">{profile?.name}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Email</Label>
                <p className="font-medium">{profile?.email}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Student ID (System Generated)</Label>
                <p className="font-medium mono">{profile?.roll_number}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Roll Number</Label>
                <p className="font-medium mono">{profile?.register_number || '-'}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Department</Label>
                <p className="font-medium">{profile?.department_name}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Batch</Label>
                <p className="font-medium">{profile?.batch}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Semester</Label>
                <p className="font-medium">{profile?.semester}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Section</Label>
                <p className="font-medium">{profile?.section || '-'}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">CGPA</Label>
                <p className="font-medium mono text-emerald-600">{profile?.cgpa?.toFixed(2) || '0.00'}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Timetable Page
function TimetablePage() {
  const [timetable, setTimetable] = useState([]);
  const [loading, setLoading] = useState(true);
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const periods = [1, 2, 3, 4, 5, 6, 7];

  useEffect(() => {
    loadTimetable();
  }, []);

  const loadTimetable = async () => {
    try {
      setLoading(true);
      const response = await subjectAPI.getStudentTimetable();
      console.log('Timetable data:', response.data);
      setTimetable(response.data || []);
    } catch (error) {
      console.error('Timetable load error:', error);
      toast.error(error.response?.data?.detail || 'Failed to load timetable');
      setTimetable([]);
    } finally {
      setLoading(false);
    }
  };

  const getSlot = (day, period) => {
    return timetable.find(item => item.day === day && item.period === period);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Weekly Timetable</h2>
      </div>

      <Card className="overflow-hidden border-none shadow-xl bg-background/50 backdrop-blur-sm">
        <CardContent className="p-0">
          <div className="overflow-x-auto pb-4">
            <table className="w-full border-collapse min-w-[1200px]">
              <thead>
                <tr className="bg-primary/5">
                  <th className="p-4 border-r border-b border-muted font-bold text-muted-foreground w-24 text-left">Day</th>
                  {periods.map(p => (
                    <th key={p} className="p-4 border-b border-muted font-bold text-center min-w-[160px]">
                      <p className="text-sm">Period {p}</p>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {days.map(day => (
                  <tr key={day} className="hover:bg-muted/30 transition-colors h-32">
                    <td className="p-4 border-r border-b border-muted font-semibold bg-primary/5 text-primary align-middle">
                      {day}
                    </td>
                    {periods.map(period => {
                      const slot = getSlot(day, period);
                      const now = new Date();
                      const currentTime = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
                      const isCurrentDay = now.toLocaleDateString('en-US', { weekday: 'long' }) === day;
                      const isCurrentPeriod = isCurrentDay && slot && currentTime >= slot.start_time && currentTime <= slot.end_time;
                      
                      return (
                        <td key={period} className={`p-2 border-b border-muted align-top ${isCurrentPeriod ? 'bg-primary/5' : ''}`}>
                          {slot ? (
                            <div className={`h-full p-3 rounded-lg bg-white dark:bg-muted/20 border border-primary/10 flex flex-col justify-between hover:shadow-md transition-all group border-l-4 ${slot.subject_type === 'lab' ? 'border-l-emerald-500' : 'border-l-primary'}`}>
                              <div>
                                <h4 className="font-bold text-sm text-primary leading-tight group-hover:text-primary/80 transition-colors line-clamp-2">
                                  {slot.subject}
                                </h4>
                                <div className="flex items-center gap-1.5 mt-1">
                                  <p className="text-[10px] mono text-muted-foreground">
                                    {slot.subject_code}
                                  </p>
                                  <Badge variant="outline" className={`text-[8px] h-3.5 px-1 ${slot.subject_type === 'lab' ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 'bg-blue-50 text-blue-700 border-blue-100'}`}>
                                    {slot.subject_type === 'lab' ? 'LAB' : 'THEORY'}
                                  </Badge>
                                </div>
                              </div>
                              <div className="mt-2 pt-2 border-t border-primary/5">
                                <p className="text-[10px] font-medium text-muted-foreground flex items-center gap-1">
                                  <Users className="h-3 w-3" />
                                  {slot.faculty || 'Faculty'}
                                </p>
                                <p className="text-[9px] text-muted-foreground mt-1 tabular-nums flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  {slot.start_time} - {slot.end_time}
                                </p>
                              </div>
                            </div>
                          ) : (
                            <div className="h-full rounded-lg border border-dashed border-muted flex items-center justify-center bg-muted/5 opacity-40">
                              <span className="text-[10px] text-muted-foreground font-medium italic">Free Period</span>
                            </div>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function ProfilePageWrapper() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const response = await studentAPI.getMyProfile();
        setProfile(response.data);
      } catch (error) {
        console.error('Error loading profile:', error);
      } finally {
        setLoading(false);
      }
    };
    loadProfile();
  }, []);

  return <ProfilePage profile={profile} loading={loading} />;
}

export default function StudentDashboard() {
  const { user } = useAuth();
  return (
    <DashboardLayout sidebarItems={sidebarItems} title="Student Portal">
      <Routes>
        <Route index element={<DashboardOverview />} />
        <Route path="attendance" element={<AttendancePage />} />
        <Route path="timetable" element={<TimetablePage />} />
        <Route path="marks" element={<MarksPage />} />
        <Route path="cgpa" element={<CGPAPage />} />
        <Route path="cgpa-calculator" element={<CGPACalculator />} />
        <Route path="fees" element={<FeesPage />} />
        <Route path="documents" element={<DocumentsPage />} />
        <Route path="grievances" element={<GrievancesPage />} />
        <Route path="leave" element={<ApplyLeavePage />} />
        <Route path="announcements" element={<AnnouncementsPage />} />
        <Route path="communications" element={<Communications userRole="student" userId={user?.id} />} />
        <Route path="settings" element={<SettingsPageWrapper />} />
        <Route path="profile" element={<ProfilePageWrapper />} />
      </Routes>
    </DashboardLayout>
  );
}
