import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    User, GraduationCap, FileText, Users, DollarSign,
    ArrowLeft, Mail, Phone, MapPin, Calendar,
    CheckCircle2, AlertCircle, Clock, History, CreditCard
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { studentAPI, feeAPI, enhancedStudentAPI } from '../../services/api';
import { EnhancedStudentForm } from '../../components/ui/EnhancedStudentForm';
import { toast } from 'sonner';
import { formatCurrency, formatDateTime, getStatusColor, getYearLabel } from '../../lib/utils';

export default function StudentDetailsPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [student, setStudent] = useState(null);
    const [feeData, setFeeData] = useState({ pending: [], payments: [] });
    const [loading, setLoading] = useState(true);
    const [showEditForm, setShowEditForm] = useState(false);

    const loadData = React.useCallback(async () => {
        try {
            const [studentRes, pendingFeesRes, paymentsRes] = await Promise.all([
                enhancedStudentAPI.getProfile(id),
                feeAPI.getPending({ student_id: id }),
                feeAPI.getPayments({ student_id: id })
            ]);

            const fullData = studentRes.data;
            const flattenedStudent = {
                ...fullData.student,
                ...fullData.user,
                department_name: fullData.department_name,
                documents: fullData.documents
            };

            setStudent(flattenedStudent);
            setFeeData({
                pending: pendingFeesRes.data || [],
                payments: paymentsRes.data || []
            });
        } catch (error) {
            console.error('Error loading student details:', error);
            toast.error('Failed to load student details');
        } finally {
            setLoading(false);
        }
    }, [id]);

    useEffect(() => {
        loadData();
    }, [id, loadData]);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
        );
    }

    if (!student) {
        return (
            <div className="p-8 text-center">
                <h2 className="text-2xl font-bold">Student not found</h2>
                <Button variant="ghost" className="mt-4" onClick={() => navigate('/admin/students')}>
                    <ArrowLeft className="mr-2 h-4 w-4" /> Back to Students
                </Button>
            </div>
        );
    }

    const totalFees = feeData.pending.reduce((acc, f) => acc + f.amount, 0) +
        feeData.payments.reduce((acc, p) => p.status === 'completed' ? acc + p.amount : acc, 0);
    const totalPaid = feeData.payments.reduce((acc, p) => p.status === 'completed' ? acc + p.amount : acc, 0);
    const totalPending = feeData.pending.reduce((acc, f) => acc + f.amount, 0);

    const handlePrint = () => {
        window.open(`${process.env.REACT_APP_API_URL || 'http://localhost:8000/api'}/students/${id}/admission-form`, '_blank');
    };

    return (
        <div className="space-y-6 pb-20">
            <EnhancedStudentForm
                isOpen={showEditForm}
                onClose={() => setShowEditForm(false)}
                onSuccess={loadData}
                editStudent={student}
            />
            {/* Header / Navigation */}
            <div className="flex items-center justify-between">
                <Button variant="ghost" onClick={() => navigate('/admin/students')}>
                    <ArrowLeft className="mr-2 h-4 w-4" /> Back
                </Button>
                <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => setShowEditForm(true)}>Edit Profile</Button>
                    <Button variant="default" size="sm" onClick={handlePrint}>Print Admission Form</Button>
                </div>
            </div>

            {/* Profile Header Card */}
            <Card className="border-0 bg-gradient-to-br from-primary/10 via-background to-background">
                <CardContent className="pt-6">
                    <div className="flex flex-col md:flex-row gap-6 items-center md:items-start text-center md:text-left">
                        <div className="w-32 h-32 rounded-2xl bg-primary/20 flex items-center justify-center overflow-hidden border-4 border-white shadow-xl">
                            <User className="w-16 h-16 text-primary" />
                        </div>
                        <div className="flex-1 space-y-2">
                            <div className="flex flex-wrap items-center gap-2 justify-center md:justify-start">
                                <h1 className="text-3xl font-bold">{student.name}</h1>
                                <Badge variant="secondary" className="bg-emerald-100 text-emerald-700 hover:bg-emerald-100 uppercase tracking-wider text-[10px] py-0">Active</Badge>
                            </div>
                            <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground justify-center md:justify-start">
                                <span className="flex items-center gap-1.5">< GraduationCap className="w-4 h-4" /> {student.roll_number}</span>
                                <span className="flex items-center gap-1.5">< Mail className="w-4 h-4" /> {student.email}</span>
                                <span className="flex items-center gap-1.5">< Phone className="w-4 h-4" /> {student.mobile_number || 'N/A'}</span>
                            </div>
                            <div className="pt-4 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl">
                                <div className="p-3 rounded-xl bg-white/50 border backdrop-blur-sm">
                                    <p className="text-[10px] uppercase text-muted-foreground font-semibold">Department</p>
                                    <p className="font-bold text-sm truncate">{student.department_name}</p>
                                </div>
                                <div className="p-3 rounded-xl bg-white/50 border backdrop-blur-sm">
                                    <p className="text-[10px] uppercase text-muted-foreground font-semibold">Year / Sem</p>
                                    <p className="font-bold text-sm">{getYearLabel(student.semester)} / Sem {student.semester}</p>
                                </div>
                                <div className="p-3 rounded-xl bg-white/50 border backdrop-blur-sm">
                                    <p className="text-[10px] uppercase text-muted-foreground font-semibold">Batch</p>
                                    <p className="font-bold text-sm">{student.batch}</p>
                                </div>
                                <div className="p-3 rounded-xl bg-white/50 border backdrop-blur-sm">
                                    <p className="text-[10px] uppercase text-muted-foreground font-semibold">CGPA</p>
                                    <p className="font-bold text-sm text-emerald-600">{(student.cgpa && student.cgpa > 0) ? student.cgpa.toFixed(2) : 'N/A'}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Main Content Tabs */}
            <Tabs defaultValue="basic" className="space-y-4">
                <TabsList className="bg-muted p-1 rounded-xl">
                    <TabsTrigger value="basic" className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">Basic Info</TabsTrigger>
                    <TabsTrigger value="personal" className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">Personal</TabsTrigger>
                    <TabsTrigger value="academic" className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">Academic</TabsTrigger>
                    <TabsTrigger value="identity" className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">Identity</TabsTrigger>
                    <TabsTrigger value="parents" className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">Parents</TabsTrigger>
                    <TabsTrigger value="fees" className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">Fees</TabsTrigger>
                </TabsList>

                {/* Basic Info Tab */}
                <TabsContent value="basic">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Card>
                            <CardHeader className="pb-3 border-b mb-3">
                                <CardTitle className="text-base flex items-center gap-2"><User className="h-4 w-4" /> Admission Details</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <DetailRow label="Register Number" value={student.register_number} />
                                <DetailRow label="Program Type" value={student.program_type || 'N/A'} />
                                <DetailRow label="Admission Type" value={student.admission_type || 'N/A'} />
                                <DetailRow label="Admission Quota" value={student.admission_quota || 'N/A'} />
                                <DetailRow label="Batch" value={student.batch} />
                                <DetailRow label="Regulation" value={student.regulation || 'R2023'} />
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-3 border-b mb-3">
                                <CardTitle className="text-base flex items-center gap-2"><MapPin className="h-4 w-4" /> Contact Information</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <DetailRow label="Primary Email" value={student.email} />
                                <DetailRow label="Mobile Number" value={student.mobile_number} />
                                <DetailRow label="Alternate Mobile" value={student.alternate_mobile} />
                                <DetailRow label="Permanent Address" value={student.permanent_address} isParagraph />
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Personal Details Tab */}
                <TabsContent value="personal">
                    <Card>
                        <CardContent className="pt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-4">
                                <DetailRow label="Date of Birth" value={student.date_of_birth} />
                                <DetailRow label="Gender" value={student.gender} />
                                <DetailRow label="Blood Group" value={student.blood_group} />
                                <DetailRow label="Community" value={student.community} />
                                <DetailRow label="Aadhar Number" value={student.aadhar_number} />
                            </div>
                            <div className="space-y-4">
                                <DetailRow label="Hostel / Day Scholar" value={student.hostel_day_scholar?.replace('_', ' ')} />
                                <DetailRow label="First Graduate" value={student.is_first_graduate ? 'Yes' : 'No'} />
                                <DetailRow label="Scholarship Details" value={student.scholarship_details} isParagraph />
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Academic Tab */}
                <TabsContent value="academic" className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Card>
                            <CardHeader><CardTitle className="text-base">10th Standard</CardTitle></CardHeader>
                            <CardContent className="space-y-3">
                                <DetailRow label="School" value={student.tenth_certificate?.school_name} />
                                <DetailRow label="Board" value={student.tenth_certificate?.board} />
                                <DetailRow label="Year" value={student.tenth_certificate?.year_of_passing} />
                                <DetailRow label="Percentage" value={`${student.tenth_certificate?.percentage}%`} />
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader><CardTitle className="text-base">12th Standard</CardTitle></CardHeader>
                            <CardContent className="space-y-3">
                                <DetailRow label="School" value={student.twelfth_certificate?.school_name} />
                                <DetailRow label="Board" value={student.twelfth_certificate?.board} />
                                <DetailRow label="Year" value={student.twelfth_certificate?.year_of_passing} />
                                <DetailRow label="Cutoff" value={student.twelfth_certificate?.cutoff} />
                                <DetailRow label="Percentage" value={`${student.twelfth_certificate?.percentage}%`} />
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Identity Tab */}
                <TabsContent value="identity">
                    <Card>
                        <CardContent className="pt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-4">
                                <DetailRow label="ID Type" value={student.identity_proof?.id_type?.toUpperCase()} />
                                <DetailRow label="ID Number" value={student.identity_proof?.id_number} />
                                <DetailRow label="EMIS ID" value={student.emis_id} />
                                <DetailRow label="UMIS ID" value={student.umis_id} />
                            </div>
                            {student.identity_proof?.id_url && (
                                <div className="p-4 rounded-lg bg-muted flex items-center justify-center">
                                    <Button variant="outline" size="sm" onClick={() => window.open(student.identity_proof.id_url)}>View Document</Button>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Parents Tab */}
                <TabsContent value="parents">
                    <Card>
                        <CardContent className="pt-6 grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="space-y-4">
                                <h3 className="font-bold text-sm text-primary flex items-center gap-2">< CheckCircle2 className="h-4 w-4" /> Parent / Guardian Details</h3>
                                <DetailRow label="Parent Name" value={student.parent_name} />
                                <DetailRow label="Parent Contact" value={student.parent_phone} />
                                <div className="mt-4 pt-4 border-t space-y-4">
                                    <h3 className="font-bold text-sm text-slate-500">Secondary Info</h3>
                                    <DetailRow label="Father Name" value={student.parent_details?.father_name} />
                                    <DetailRow label="Father Contact" value={student.parent_details?.father_contact} />
                                </div>
                            </div>
                            <div className="space-y-4">
                                <h3 className="font-bold text-sm text-primary flex items-center gap-2">< CheckCircle2 className="h-4 w-4" /> Mother's Details</h3>
                                <DetailRow label="Name" value={student.parent_details?.mother_name} />
                                <DetailRow label="Occupation" value={student.parent_details?.mother_occupation} />
                                <DetailRow label="Contact" value={student.parent_details?.mother_contact} />
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Fees Tab */}
                <TabsContent value="fees" className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <Card className="bg-emerald-50 border-emerald-100">
                            <CardContent className="pt-6 flex items-center justify-between">
                                <div>
                                    <p className="text-[10px] text-emerald-600 font-bold uppercase">Total Paid</p>
                                    <p className="text-xl font-bold font-mono">{formatCurrency(totalPaid)}</p>
                                </div>
                                <CheckCircle2 className="h-8 w-8 text-emerald-500 opacity-50" />
                            </CardContent>
                        </Card>
                        <Card className="bg-rose-50 border-rose-100">
                            <CardContent className="pt-6 flex items-center justify-between">
                                <div>
                                    <p className="text-[10px] text-rose-600 font-bold uppercase">Pending</p>
                                    <p className="text-xl font-bold font-mono">{formatCurrency(totalPending)}</p>
                                </div>
                                <AlertCircle className="h-8 w-8 text-rose-500 opacity-50" />
                            </CardContent>
                        </Card>
                        <Card className="bg-blue-50 border-blue-100">
                            <CardContent className="pt-6 flex items-center justify-between">
                                <div>
                                    <p className="text-[10px] text-blue-600 font-bold uppercase">Total Due</p>
                                    <p className="text-xl font-bold font-mono">{formatCurrency(totalFees)}</p>
                                </div>
                                <DollarSign className="h-8 w-8 text-blue-500 opacity-50" />
                            </CardContent>
                        </Card>
                    </div>

                    <Card>
                        <CardHeader className="pb-0"><CardTitle className="text-base flex items-center gap-2"><History className="h-4 w-4" /> Payment History</CardTitle></CardHeader>
                        <CardContent>
                            {feeData.payments.length === 0 ? (
                                <p className="text-center py-10 text-muted-foreground text-sm">No payment history found</p>
                            ) : (
                                <div className="overflow-x-auto mt-4">
                                    <table className="w-full text-sm">
                                        <thead>
                                            <tr className="border-b text-muted-foreground">
                                                <th className="text-left font-medium py-2">Date</th>
                                                <th className="text-left font-medium py-2">Fee Name</th>
                                                <th className="text-right font-medium py-2">Amount</th>
                                                <th className="text-center font-medium py-2">Status</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {feeData.payments.map(p => (
                                                <tr key={p.id} className="border-b hover:bg-muted/50">
                                                    <td className="py-3 font-mono text-xs">{formatDateTime(p.payment_date)}</td>
                                                    <td className="py-3 font-medium">{p.fee_name}</td>
                                                    <td className="py-3 text-right font-bold font-mono">{formatCurrency(p.amount)}</td>
                                                    <td className="py-3 text-center">
                                                        <Badge className={getStatusColor(p.status)}>{p.status?.replace('_', ' ')}</Badge>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {feeData.pending.length > 0 && (
                        <Card className="border-rose-200">
                            <CardHeader className="pb-0"><CardTitle className="text-base text-rose-600 flex items-center gap-2"><Clock className="h-4 w-4" /> Pending Fees</CardTitle></CardHeader>
                            <CardContent className="space-y-2 mt-4">
                                {feeData.pending.map(f => (
                                    <div key={f.id} className="flex items-center justify-between p-3 rounded-lg bg-rose-50/50 border border-rose-100">
                                        <div>
                                            <p className="font-bold text-sm">{f.name}</p>
                                            <p className="text-[10px] text-muted-foreground uppercase">{f.category}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="font-bold font-mono text-sm">{formatCurrency(f.amount)}</p>
                                            <p className="text-[10px] text-rose-600">Due: {f.due_date || 'N/A'}</p>
                                        </div>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>
                    )}
                </TabsContent>
            </Tabs>
        </div>
    );
}

function DetailRow({ label, value, isParagraph = false, isFull = false }) {
    if (!value && value !== 0) return null;
    return (
        <div className={`flex ${isFull ? 'flex-col' : 'items-start justify-between'} gap-1`}>
            <span className="text-xs text-muted-foreground shrink-0">{label}</span>
            <span className={`text-sm font-medium ${isParagraph ? 'bg-muted/30 p-2 rounded-lg text-xs leading-relaxed mt-1 block w-full' : ''}`}>
                {value}
            </span>
        </div>
    );
}
