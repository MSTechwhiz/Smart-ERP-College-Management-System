import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useParams } from 'react-router-dom';
import {
  LayoutDashboard,
  Calendar,
  ClipboardCheck,
  FileSpreadsheet,
  Users,
  BookOpen,
  Settings,
  Clock,
  Upload,
  Eye,
  CheckCircle,
  Megaphone,
  MessageSquare
} from 'lucide-react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import { Checkbox } from '../../components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../../components/ui/dialog';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '../../components/ui/tabs';
import {
  facultyAPI,
  studentAPI,
  subjectAPI,
  attendanceAPI,
  marksAPI,
  uploadAPI,
  announcementAPI,
  grievanceAPI
} from '../../services/api';
import { toast } from 'sonner';
import { useAuth } from '../../context/AuthContext';
import { formatDate } from '../../lib/utils';

import AnnouncementsPage from '../common/AnnouncementsPage';
import { Communications } from '../shared/Communications';

// Dashboard Overview
function DashboardOverview({ deptCode }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const getDeptPath = (path) => `/faculty/${deptCode}${path}`;
  const [profile, setProfile] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [students, setStudents] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadDashboardData = async () => {
    try {
      const [profileRes, subjectsRes, studentsRes, annRes] = await Promise.all([
        facultyAPI.getMyProfile(),
        subjectAPI.getMappings({ faculty_id: user?.id }),
        studentAPI.getAll({ department_id: user?.department_id }),
        announcementAPI.getAll().catch(() => ({ data: [] }))
      ]);
      setProfile(profileRes.data);
      setSubjects(subjectsRes.data);
      setStudents(studentsRes.data.students || []);
      setAnnouncements(annRes.data.slice(0, 3));
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

  return (
    <div className="space-y-6">
      {/* Welcome Card */}
      <Card className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white border-0">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-1">Welcome, {profile?.name}</h2>
              <p className="opacity-90">{profile?.designation}</p>
              <p className="text-sm opacity-75 mt-1 mono">{profile?.employee_id}</p>
            </div>
            {profile?.is_class_incharge && (
              <Badge className="bg-white/20 text-white">
                Class Incharge: {profile?.incharge_class}
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="stat-card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate(getDeptPath('/subjects'))}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Assigned Subjects</p>
                <p className="text-3xl font-bold mono">{subjects.length}</p>
              </div>
              <BookOpen className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="stat-card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate(getDeptPath('/students'))}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">My Students</p>
                <p className="text-3xl font-bold mono">{students.length}</p>
              </div>
              <Users className="h-8 w-8 text-emerald-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="stat-card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate(getDeptPath('/attendance'))}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Pending Actions</p>
                <p className="text-3xl font-bold mono">0</p>
              </div>
              <ClipboardCheck className="h-8 w-8 text-amber-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-3">
            <Button variant="outline" className="h-auto py-4 flex-col gap-2" data-testid="mark-attendance-btn" onClick={() => navigate(getDeptPath('/attendance'))}>
              <ClipboardCheck className="h-5 w-5" />
              <span>Mark Attendance</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col gap-2" data-testid="enter-marks-btn" onClick={() => navigate(getDeptPath('/marks'))}>
              <FileSpreadsheet className="h-5 w-5" />
              <span>Enter Marks</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col gap-2" data-testid="view-students-btn" onClick={() => navigate(getDeptPath('/students'))}>
              <Users className="h-5 w-5" />
              <span>View Students</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col gap-2" data-testid="bulk-upload-btn" onClick={() => navigate(getDeptPath('/upload'))}>
              <Upload className="h-5 w-5" />
              <span>Bulk Upload</span>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>My Subjects</CardTitle>
          </CardHeader>
          <CardContent>
            {subjects.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                No subjects assigned. Contact your HOD.
              </p>
            ) : (
              <div className="space-y-3">
                {subjects.map((subj, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <div>
                      <p className="font-medium">{subj.subject_name}</p>
                      <p className="text-sm text-muted-foreground mono">{subj.subject_code}</p>
                    </div>
                    <Badge variant="outline">Section {subj.section}</Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Announcements Section */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-lg font-bold">Recent Announcements</CardTitle>
          <Megaphone className="h-5 w-5 text-primary" />
        </CardHeader>
        <CardContent>
          {announcements.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-6">No recent announcements</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {announcements.map((ann) => (
                <div key={ann.id} className="p-4 rounded-lg bg-muted/30 border border-muted hover:border-primary/50 transition-colors cursor-pointer" onClick={() => navigate(getDeptPath('/announcements'))}>
                  <div className="flex justify-between items-start mb-2">
                    <Badge variant="outline" className="text-[10px]">{ann.type}</Badge>
                    <span className="text-[10px] text-muted-foreground">{formatDate(ann.publish_date)}</span>
                  </div>
                  <h4 className="font-semibold text-sm mb-1 line-clamp-1">{ann.title}</h4>
                  <p className="text-xs text-muted-foreground line-clamp-2">{ann.content}</p>
                </div>
              ))}
            </div>
          )}
          {announcements.length > 0 && (
            <div className="text-center mt-4">
              <Button
                variant="link"
                className="text-primary"
                onClick={() => navigate(getDeptPath('/announcements'))}
              >
                View All Announcements
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Attendance Page
function AttendancePage() {
  const { user } = useAuth();
  const [subjects, setSubjects] = useState([]);
  const [students, setStudents] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [attendance, setAttendance] = useState({});
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadSubjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (selectedSubject) {
      loadStudents();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSubject]);

  const loadSubjects = async () => {
    setLoading(true);
    try {
      const response = await subjectAPI.getMappings({ faculty_id: user?.id });
      setSubjects(response.data);
    } catch (error) {
      toast.error('Failed to load subjects');
    } finally {
      setLoading(false);
    }
  };

  const loadStudents = async () => {
    try {
      const response = await studentAPI.getAll({ department_id: user?.department_id });
      const studentsData = response.data.students || [];
      setStudents(studentsData);
      // Initialize attendance state
      const initial = {};
      studentsData.forEach(s => initial[s.id] = 'present');
      setAttendance(initial);
    } catch (error) {
      toast.error('Failed to load students');
    }
  };

  const handleSubmit = async () => {
    if (!selectedSubject) {
      toast.error('Please select a subject');
      return;
    }

    setSubmitting(true);
    try {
      const records = Object.entries(attendance).map(([studentId, status]) => ({
        student_id: studentId,
        status
      }));

      await attendanceAPI.markBulk({
        subject_id: selectedSubject,
        date,
        records
      });

      toast.success('Attendance marked successfully');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to mark attendance');
    } finally {
      setSubmitting(false);
    }
  };

  const markAllPresent = () => {
    const newAttendance = {};
    students.forEach(s => newAttendance[s.id] = 'present');
    setAttendance(newAttendance);
  };

  const markAllAbsent = () => {
    const newAttendance = {};
    students.forEach(s => newAttendance[s.id] = 'absent');
    setAttendance(newAttendance);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Mark Attendance</h2>

      <Card>
        <CardHeader>
          <CardTitle>Select Class</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Subject</Label>
              <Select value={selectedSubject} onValueChange={setSelectedSubject}>
                <SelectTrigger data-testid="attendance-subject-select">
                  <SelectValue placeholder="Select subject" />
                </SelectTrigger>
                <SelectContent>
                  {subjects.map((subj) => (
                    <SelectItem key={subj.id} value={subj.subject_id}>
                      {subj.subject_name} ({subj.section})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Date</Label>
              <Input
                type="date"
                data-testid="attendance-date-input"
                value={date}
                onChange={(e) => setDate(e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {selectedSubject && students.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Student List</CardTitle>
                <CardDescription>Mark attendance for each student</CardDescription>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={markAllPresent} data-testid="mark-all-present-btn">
                  <CheckCircle className="h-4 w-4 mr-1" />
                  All Present
                </Button>
                <Button variant="outline" size="sm" onClick={markAllAbsent} data-testid="mark-all-absent-btn">
                  All Absent
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {students.map((student) => (
                <div key={student.id} className="flex items-center justify-between p-3 rounded-lg border">
                  <div>
                    <p className="font-medium">{student.name}</p>
                    <p className="text-sm text-muted-foreground mono">{student.roll_number}</p>
                  </div>
                  <Select
                    value={attendance[student.id] || 'present'}
                    onValueChange={(value) => setAttendance({ ...attendance, [student.id]: value })}
                  >
                    <SelectTrigger className="w-32" data-testid={`attendance-${student.id}`}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="present">Present</SelectItem>
                      <SelectItem value="absent">Absent</SelectItem>
                      <SelectItem value="od">OD</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              ))}
            </div>
            <Button
              className="w-full mt-4"
              onClick={handleSubmit}
              disabled={submitting}
              data-testid="submit-attendance-btn"
            >
              {submitting ? 'Submitting...' : 'Submit Attendance'}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// Marks Entry Page
function MarksEntryPage() {
  const { user } = useAuth();
  const [subjects, setSubjects] = useState([]);
  const [students, setStudents] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [examType, setExamType] = useState('cia1');
  const [academicYear, setAcademicYear] = useState('2024-25');
  const [semester, setSemester] = useState(5);
  const [marks, setMarks] = useState({});
  const [allMarks, setAllMarks] = useState([]); // All stored marks for classification
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadSubjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (selectedSubject) {
      loadStudents();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSubject]);

  const loadSubjects = async () => {
    try {
      const response = await subjectAPI.getMappings({ faculty_id: user?.id });
      setSubjects(response.data);
    } catch (error) {
      toast.error('Failed to load subjects');
    }
  };

  const loadStudents = async () => {
    try {
      setLoading(true);
      const [studentsRes, marksRes] = await Promise.all([
        studentAPI.getAll({ department_id: user?.department_id }),
        marksAPI.getAll({ department_id: user?.department_id })
      ]);
      const studentsData = studentsRes.data.students || [];
      setStudents(studentsData);
      setAllMarks(marksRes.data || []);
      // Initialize marks state
      const initial = {};
      studentsData.forEach(s => initial[s.id] = '');
      setMarks(initial);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const getLearnerClassification = (studentId, currentVal) => {
    const studentMarks = allMarks.filter(m => m.student_id === studentId);
    let total = 0;
    let count = 0;

    studentMarks.forEach(m => {
      const exams = ['cia1', 'cia2', 'cia3', 'cia4', 'model_exam', 'assignment', 'lab', 'semester_exam'];
      exams.forEach(exam => {
        // If this is the exam we are currently editing, use the current input value
        if (m.subject_id === selectedSubject && exam === examType) {
          return; // Skip stored value for currently edited field
        }
        if (m[exam] !== undefined && m[exam] !== null) {
          total += m[exam];
          count++;
        }
      });
    });

    // Add current input value if it exists
    if (currentVal !== '' && !isNaN(parseFloat(currentVal))) {
      total += parseFloat(currentVal);
      count++;
    }

    const avg = count > 0 ? total / count : 0;
    
    if (avg === 0) return { type: 'Unclassified', color: 'bg-slate-100 text-slate-800' };
    if (avg > 70) return { type: 'Fast Learner', color: 'bg-emerald-100 text-emerald-800' };
    if (avg > 60) return { type: 'Medium Learner', color: 'bg-blue-100 text-blue-800' };
    if (avg >= 50) return { type: 'Average Learner', color: 'bg-amber-100 text-amber-800' };
    return { type: 'Slow Learner', color: 'bg-rose-100 text-rose-800' };
  };

  const handleSubmit = async () => {
    if (!selectedSubject) {
      toast.error('Please select a subject');
      return;
    }

    const records = Object.entries(marks)
      .filter(([_, value]) => value !== '' && !isNaN(parseFloat(value)))
      .map(([studentId, marksValue]) => ({
        student_id: studentId,
        marks: parseFloat(marksValue)
      }));

    if (records.length === 0) {
      toast.error('Please enter marks for at least one student');
      return;
    }

    setSubmitting(true);
    try {
      await marksAPI.enterBulk({
        subject_id: selectedSubject,
        academic_year: academicYear,
        semester,
        exam_type: examType,
        records
      });

      toast.success('Marks entered successfully');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to enter marks');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Enter Marks</h2>

      <Card>
        <CardHeader>
          <CardTitle>Select Exam</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label>Subject</Label>
              <Select value={selectedSubject} onValueChange={setSelectedSubject}>
                <SelectTrigger data-testid="marks-subject-select">
                  <SelectValue placeholder="Select subject" />
                </SelectTrigger>
                <SelectContent>
                  {subjects.map((subj) => (
                    <SelectItem key={subj.id} value={subj.subject_id}>
                      {subj.subject_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Exam Type</Label>
              <Select value={examType} onValueChange={setExamType}>
                <SelectTrigger data-testid="marks-examtype-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cia1">CIA 1</SelectItem>
                  <SelectItem value="cia2">CIA 2</SelectItem>
                  <SelectItem value="cia3">CIA 3</SelectItem>
                  <SelectItem value="cia4">CIA 4</SelectItem>
                  <SelectItem value="model_exam">Model Exam</SelectItem>
                  <SelectItem value="assignment">Assignment</SelectItem>
                  <SelectItem value="lab">Lab</SelectItem>
                  <SelectItem value="semester_exam">Semester Exam</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Academic Year</Label>
              <Input
                data-testid="marks-year-input"
                value={academicYear}
                onChange={(e) => setAcademicYear(e.target.value)}
                placeholder="2024-25"
              />
            </div>
            <div className="space-y-2">
              <Label>Semester</Label>
              <Input
                type="number"
                min="1"
                max="8"
                data-testid="marks-semester-input"
                value={semester}
                onChange={(e) => setSemester(parseInt(e.target.value))}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {selectedSubject && students.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Enter Marks</CardTitle>
            <CardDescription>Enter marks out of 100</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {students.map((student) => (
                <div key={student.id} className="flex items-center justify-between p-3 rounded-lg border">
                  <div>
                    <p className="font-medium">{student.name}</p>
                    <p className="text-sm text-muted-foreground mono">{student.roll_number}</p>
                  </div>
                  <div className="flex-1 px-4 text-right">
                    <Badge variant="secondary" className={getLearnerClassification(student.id, marks[student.id]).color}>
                      {getLearnerClassification(student.id, marks[student.id]).type}
                    </Badge>
                  </div>
                  <Input
                    type="number"
                    min="0"
                    max="100"
                    className="w-24"
                    placeholder="Marks"
                    data-testid={`marks-${student.id}`}
                    value={marks[student.id] || ''}
                    onChange={(e) => setMarks({ ...marks, [student.id]: e.target.value })}
                  />
                </div>
              ))}
            </div>
            <Button
              className="w-full mt-4"
              onClick={handleSubmit}
              disabled={submitting}
              data-testid="submit-marks-btn"
            >
              {submitting ? 'Submitting...' : 'Submit Marks'}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// Today's Classes Page
function TodayClassesPage() {
  const { user } = useAuth();
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSubjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadSubjects = async () => {
    try {
      const response = await subjectAPI.getMappings({ faculty_id: user?.id });
      setSubjects(response.data);
    } catch (error) {
      toast.error('Failed to load subjects');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  // Mock schedule - in a real app, this would come from a timetable API
  const schedule = subjects.map((subj, idx) => ({
    ...subj,
    time: `${9 + idx * 2}:00 - ${10 + idx * 2}:00`,
    room: `Room ${101 + idx}`
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Today's Classes</h2>
        <p className="text-muted-foreground">{new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
      </div>

      <div className="space-y-4">
        {schedule.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              No classes scheduled for today
            </CardContent>
          </Card>
        ) : (
          schedule.map((cls, idx) => (
            <Card key={idx} className="card-interactive">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold">{cls.subject_name}</h3>
                    <p className="text-sm text-muted-foreground mono">{cls.subject_code}</p>
                    <div className="flex gap-4 mt-2">
                      <span className="text-sm flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        {cls.time}
                      </span>
                      <span className="text-sm">{cls.room}</span>
                    </div>
                  </div>
                  <Badge variant="outline">Section {cls.section}</Badge>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

// My Students Page
function MyStudentsPage() {
  const { user } = useAuth();
  const [students, setStudents] = useState([]);
  const [marks, setMarks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewStudent, setViewStudent] = useState(null);
  const [selectedYear, setSelectedYear] = useState('all');
  const [learnerFilter, setLearnerFilter] = useState('all');

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [studentsRes, marksRes] = await Promise.all([
        studentAPI.getAll({ department_id: user?.department_id }),
        marksAPI.getAll({ department_id: user?.department_id })
      ]);
      setStudents(studentsRes.data.students || []);
      setMarks(marksRes.data || []);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const getStudentMetrics = (studentId) => {
    const studentMarks = marks.filter(m => m.student_id === studentId);
    if (!studentMarks.length) return { cgpa: 0, learnerType: 'Slow Learner', avgMarks: 0 };

    let totalMarks = 0;
    let count = 0;

    studentMarks.forEach(m => {
      const exams = ['cia1', 'cia2', 'cia3', 'cia4', 'model_exam', 'assignment', 'lab', 'semester_exam'];
      exams.forEach(exam => {
        if (m[exam] !== undefined && m[exam] !== null) {
          totalMarks += m[exam];
          count++;
        }
      });
    });

    const avgMarks = count > 0 ? totalMarks / count : 0;
    const cgpa = avgMarks / 10;

    let learnerType = 'Slow Learner';
    if (avgMarks > 70) learnerType = 'Fast Learner';
    else if (avgMarks > 60) learnerType = 'Medium Learner';
    else if (avgMarks >= 50) learnerType = 'Average Learner';

    return { cgpa, learnerType, avgMarks };
  };

  const filteredStudents = students.filter(s => {
    // 1. Year Filter
    if (selectedYear !== 'all') {
      const sem = parseInt(s.semester);
      const year = Math.ceil(sem / 2);
      if (parseInt(selectedYear) !== year) return false;
    }
    
    // 2. Learner Filter
    if (learnerFilter !== 'all') {
      const metrics = getStudentMetrics(s.id);
      if (metrics.learnerType.toLowerCase().split(' ')[0] !== learnerFilter) return false;
    }
    
    return true;
  });

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">My Students</h2>

      {/* View Student Dialog */}
      <Dialog open={!!viewStudent} onOpenChange={() => setViewStudent(null)}>
        <DialogContent className="max-w-md" aria-describedby={undefined}>
          <DialogHeader>
            <DialogTitle>Student Details</DialogTitle>
          </DialogHeader>
          {viewStudent && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Name</p>
                <p className="font-medium">{viewStudent.name}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="font-medium">{viewStudent.email}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Student ID (System Generated)</p>
                <p className="font-medium mono">{viewStudent.roll_number}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Roll Number</p>
                <p className="font-medium mono">{viewStudent.register_number || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Batch</p>
                <p className="font-medium">{viewStudent.batch}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Semester</p>
                <p className="font-medium">{viewStudent.semester}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">CGPA</p>
                <p className="font-medium mono">
                  {(!viewStudent.cgpa || viewStudent.cgpa === 0) ? 'N/A' : viewStudent.cgpa.toFixed(2)}
                </p>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <div className="flex flex-col sm:flex-row gap-4 items-end">
        <div className="flex-1">
          <Tabs value={selectedYear} onValueChange={setSelectedYear} className="w-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="all">All</TabsTrigger>
              <TabsTrigger value="1">1st Yr</TabsTrigger>
              <TabsTrigger value="2">2nd Yr</TabsTrigger>
              <TabsTrigger value="3">3rd Yr</TabsTrigger>
              <TabsTrigger value="4">Final</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
        <div className="w-full sm:w-64 space-y-2">
          <Label>Learner Filter</Label>
          <Select value={learnerFilter} onValueChange={setLearnerFilter}>
            <SelectTrigger>
              <SelectValue placeholder="All Students" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Students</SelectItem>
              <SelectItem value="slow">Slow Learners</SelectItem>
              <SelectItem value="average">Average Learners</SelectItem>
              <SelectItem value="medium">Medium Learners</SelectItem>
              <SelectItem value="fast">Fast Learners</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <Card>
        <CardContent className="pt-6">
          {filteredStudents.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No students found for this year</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium">Reg No</th>
                    <th className="text-left py-3 px-4 font-medium">Name</th>
                    <th className="text-left py-3 px-4 font-medium">Semester</th>
                    <th className="text-left py-3 px-4 font-medium">CGPA</th>
                    <th className="text-left py-3 px-4 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredStudents.map((student) => {
                    const metrics = getStudentMetrics(student.id);
                    return (
                      <tr key={student.id} className="border-b hover:bg-muted/50">
                        <td className="py-3 px-4 mono">{student.roll_number}</td>
                        <td className="py-3 px-4">{student.name}</td>
                        <td className="py-3 px-4">{student.semester}</td>
                        <td className="py-3 px-4 mono font-medium">
                          {metrics.cgpa > 0 ? metrics.cgpa.toFixed(2) : '0.00'}
                        </td>
                        <td className="py-3 px-4">
                          <Button variant="ghost" size="sm" onClick={() => setViewStudent(student)} data-testid={`view-student-${student.id}`}>
                            <Eye className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Subjects Page
function SubjectsPage() {
  const { user } = useAuth();
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSubjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadSubjects = async () => {
    try {
      const response = await subjectAPI.getMappings({ faculty_id: user?.id });
      setSubjects(response.data);
    } catch (error) {
      toast.error('Failed to load subjects');
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
      <h2 className="text-2xl font-bold">My Subjects</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {subjects.length === 0 ? (
          <Card className="col-span-full">
            <CardContent className="py-8 text-center text-muted-foreground">
              No subjects assigned. Contact your HOD for subject allocation.
            </CardContent>
          </Card>
        ) : (
          subjects.map((subj, idx) => (
            <Card key={idx} className="card-interactive">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="h-12 w-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                    <BookOpen className="h-6 w-6 text-blue-600" />
                  </div>
                  <Badge variant="outline">Section {subj.section}</Badge>
                </div>
                <h3 className="font-semibold">{subj.subject_name}</h3>
                <p className="text-sm text-muted-foreground mono mb-2">{subj.subject_code}</p>
                <div className="flex gap-4 text-xs text-muted-foreground">
                  <span>Semester: {subj.semester}</span>
                  <span>Year: {subj.academic_year}</span>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

// Bulk Upload Page
function BulkUploadPage() {
  const [uploading, setUploading] = useState(false);
  const [selectedType, setSelectedType] = useState('marks');
  const [result, setResult] = useState(null);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setResult(null);

    try {
      let response;
      switch (selectedType) {
        case 'marks':
          response = await uploadAPI.marks(file);
          break;
        case 'attendance':
          response = await uploadAPI.attendance(file);
          break;
        default:
          throw new Error('Invalid upload type');
      }
      setResult(response.data);
      toast.success(response.data.message);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Bulk Upload</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Upload Excel File</CardTitle>
            <CardDescription>
              Upload Excel files to bulk import marks or attendance
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Data Type</Label>
              <Select value={selectedType} onValueChange={setSelectedType}>
                <SelectTrigger data-testid="upload-type-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="marks">Marks</SelectItem>
                  <SelectItem value="attendance">Attendance</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Excel File</Label>
              <Input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleUpload}
                disabled={uploading}
                data-testid="upload-file-input"
              />
            </div>

            {uploading && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                Processing...
              </div>
            )}

            {result && (
              <div className="p-4 rounded-lg bg-muted">
                <p className="font-medium mb-2">{result.message}</p>
                {result.errors?.length > 0 && (
                  <div className="mt-2 space-y-1">
                    <p className="text-sm text-destructive">Errors:</p>
                    {result.errors.slice(0, 5).map((err, idx) => (
                      <p key={idx} className="text-xs text-muted-foreground">
                        Row {err.row}: {err.error}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Template Format</CardTitle>
            <CardDescription>
              Required columns for each data type
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selectedType === 'marks' && (
              <div className="space-y-2">
                <p className="font-medium text-sm">Marks Upload Columns:</p>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>registration_number (required)</li>
                  <li>subject_code (required)</li>
                  <li>academic_year (required)</li>
                  <li>semester (required)</li>
                  <li>exam_type (required)</li>
                  <li>marks (required)</li>
                </ul>
              </div>
            )}
            {selectedType === 'attendance' && (
              <div className="space-y-2">
                <p className="font-medium text-sm">Attendance Upload Columns:</p>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>registration_number (required)</li>
                  <li>subject_code (required)</li>
                  <li>date (required, YYYY-MM-DD)</li>
                  <li>status (required: present/absent/od)</li>
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Settings Page
// Grievances Page
function GrievancesPage() {
  const { user } = useAuth();
  const [grievances, setGrievances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedGrievance, setSelectedGrievance] = useState(null);
  const [resolution, setResolution] = useState('');
  const [remarks, setRemarks] = useState('');
  const [actionType, setActionType] = useState(null); // 'resolve' or 'escalate'

  useEffect(() => {
    loadGrievances();
  }, []);

  const loadGrievances = async () => {
    try {
      const response = await grievanceAPI.getAll({
        current_level: 'faculty'
      });
      setGrievances(response.data);
    } catch (error) {
      console.error('Error loading grievances:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async () => {
    if (!resolution) {
      toast.error('Please provide a resolution');
      return;
    }
    try {
      await grievanceAPI.resolve(selectedGrievance.id, resolution);
      toast.success('Grievance resolved');
      setSelectedGrievance(null);
      setResolution('');
      loadGrievances();
    } catch (error) {
      toast.error('Failed to resolve grievance');
    }
  };

  const handleEscalate = async () => {
    try {
      await grievanceAPI.forward(selectedGrievance.id, 'hod', remarks);
      toast.success('Grievance escalated to HOD');
      setSelectedGrievance(null);
      setRemarks('');
      loadGrievances();
    } catch (error) {
      toast.error('Failed to escalate grievance');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Grievances</h2>

      <Dialog open={!!selectedGrievance} onOpenChange={() => {
        setSelectedGrievance(null);
        setActionType(null);
      }}>
        <DialogContent className="max-w-lg" aria-describedby={undefined}>
          <DialogHeader>
            <DialogTitle>{selectedGrievance?.subject}</DialogTitle>
            <DialogDescription>by {selectedGrievance?.student_name} ({selectedGrievance?.roll_number})</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm border-b pb-2">{selectedGrievance?.description}</p>

            <div className="flex gap-4">
              <Button
                variant={actionType === 'resolve' ? 'default' : 'outline'}
                className="flex-1"
                onClick={() => setActionType('resolve')}
              >
                Resolve
              </Button>
              <Button
                variant={actionType === 'escalate' ? 'destructive' : 'outline'}
                className="flex-1"
                onClick={() => setActionType('escalate')}
              >
                Escalate to HOD
              </Button>
            </div>

            {actionType === 'resolve' && (
              <div className="space-y-2">
                <Label>Resolution</Label>
                <Textarea
                  value={resolution}
                  onChange={(e) => setResolution(e.target.value)}
                  placeholder="Provide a resolution..."
                  rows={4}
                />
                <Button onClick={handleResolve} className="w-full bg-emerald-600 hover:bg-emerald-700">Submit Resolution</Button>
              </div>
            )}

            {actionType === 'escalate' && (
              <div className="space-y-2">
                <Label>Remarks for HOD</Label>
                <Textarea
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                  placeholder="Explain why this is being escalated..."
                  rows={2}
                />
                <Button onClick={handleEscalate} className="w-full" variant="destructive">Confirm Escalation</Button>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      <div className="grid grid-cols-1 gap-4">
        {grievances.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              No pending grievances at faculty level
            </CardContent>
          </Card>
        ) : (
          grievances.map((g) => (
            <Card key={g.id}>
              <CardContent className="pt-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-lg">{g.subject}</h3>
                    <p className="text-sm text-muted-foreground">From: {g.student_name} ({g.roll_number})</p>
                    <p className="mt-2 text-sm line-clamp-2">{g.description}</p>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <Badge variant="outline" className="capitalize">{g.category}</Badge>
                    <Button size="sm" onClick={() => {
                      setSelectedGrievance(g);
                      setActionType(null);
                    }}>
                      Action
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

// Settings Page - Use Shared Component
import { SettingsPage as SharedSettingsPage, ProfilePage } from '../../components/ui/SettingsPage';

function SettingsPageWrapper() {
  return <SharedSettingsPage />;
}

function ProfilePageWrapper() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const response = await facultyAPI.getMyProfile();
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

export default function FacultyDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { deptCode } = useParams();

  useEffect(() => {
    if (user && deptCode && user.department_code) {
      if (deptCode.toLowerCase() !== user.department_code.toLowerCase()) {
        toast.error('Access Denied: You can only access your own department dashboard');
        navigate(`/faculty/${user.department_code.toLowerCase()}`, { replace: true });
      }
    }
  }, [user, deptCode, navigate]);

  const dynamicSidebarItems = [
    { icon: LayoutDashboard, label: 'Dashboard', href: `/faculty/${deptCode}` },
    { icon: Calendar, label: "Today's Classes", href: `/faculty/${deptCode}/today` },
    { icon: ClipboardCheck, label: 'Attendance', href: `/faculty/${deptCode}/attendance` },
    { icon: FileSpreadsheet, label: 'Marks Entry', href: `/faculty/${deptCode}/marks` },
    { icon: Users, label: 'My Students', href: `/faculty/${deptCode}/students` },
    { icon: BookOpen, label: 'Subjects', href: `/faculty/${deptCode}/subjects` },
    { icon: Megaphone, label: 'Announcements', href: `/faculty/${deptCode}/announcements` },
    { icon: MessageSquare, label: 'Grievances', href: `/faculty/${deptCode}/grievances` },
    { icon: MessageSquare, label: 'Communications', href: `/faculty/${deptCode}/communications` },
    { icon: Upload, label: 'Bulk Upload', href: `/faculty/${deptCode}/upload` },
    { icon: Settings, label: 'Settings', href: `/faculty/${deptCode}/settings` },
  ];

  return (
    <DashboardLayout sidebarItems={dynamicSidebarItems} title={`Faculty Dashboard - ${deptCode?.toUpperCase()}`}>
      <Routes>
        <Route index element={<DashboardOverview deptCode={deptCode} />} />
        <Route path="today" element={<TodayClassesPage deptCode={deptCode} />} />
        <Route path="attendance" element={<AttendancePage deptCode={deptCode} />} />
        <Route path="marks" element={<MarksEntryPage deptCode={deptCode} />} />
        <Route path="students" element={<MyStudentsPage deptCode={deptCode} />} />
        <Route path="subjects" element={<SubjectsPage deptCode={deptCode} />} />
        <Route path="announcements" element={<AnnouncementsPage />} />
        <Route path="grievances" element={<GrievancesPage />} />
        <Route path="communications" element={<Communications userRole="faculty" userId={user?.id} />} />
        <Route path="upload" element={<BulkUploadPage deptCode={deptCode} />} />
        <Route path="settings" element={<SettingsPageWrapper deptCode={deptCode} />} />
        <Route path="profile" element={<ProfilePageWrapper deptCode={deptCode} />} />
      </Routes>
    </DashboardLayout>
  );
}
