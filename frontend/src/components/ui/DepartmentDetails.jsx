import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './card';
import { Button } from './button';
import { Badge } from './badge';
import { Progress } from './progress';
import { 
  Users, 
  Building2, 
  GraduationCap, 
  TrendingUp, 
  DollarSign, 
  ArrowLeft,
  BarChart3
} from 'lucide-react';
import { analyticsAPI } from '../../services/api';
import { toast } from 'sonner';
import { formatCurrency } from '../../lib/utils';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export function DepartmentDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      const response = await analyticsAPI.getDepartmentAnalytics(id);
      setData(response.data);
    } catch (error) {
      console.error('Department analytics error:', error);
      toast.error('Failed to load department analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!data) return (
    <div className="flex flex-col items-center justify-center h-64 gap-4">
      <p className="text-muted-foreground">Department data unavailable</p>
      <Button variant="outline" onClick={() => navigate(-1)}>Go Back</Button>
    </div>
  );

  const { department, stats, performance_trend } = data;
  const yd = stats?.year_distribution || {};

  const yearData = [
    { label: '1st Year', count: yd.year_1 || 0, color: '#3b82f6' },
    { label: '2nd Year', count: yd.year_2 || 0, color: '#8b5cf6' },
    { label: '3rd Year', count: yd.year_3 || 0, color: '#10b981' },
    { label: 'Final Year', count: yd.year_4 || 0, color: '#f59e0b' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h2 className="text-2xl font-bold">{department?.name}</h2>
          <p className="text-muted-foreground mono">{department?.code}</p>
        </div>
      </div>

      {/* Key Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Students</p>
                <p className="text-3xl font-bold">{stats?.student_count ?? 0}</p>
              </div>
              <GraduationCap className="h-8 w-8 text-blue-600 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Faculty</p>
                <p className="text-3xl font-bold">{stats?.faculty_count ?? 0}</p>
              </div>
              <Users className="h-8 w-8 text-emerald-600 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Attendance</p>
                <p className="text-3xl font-bold">{stats?.attendance_percentage ?? 0}%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-amber-600 opacity-20" />
            </div>
            <Progress value={stats?.attendance_percentage ?? 0} className="mt-3 h-1.5" />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Avg CGPA</p>
                <p className="text-3xl font-bold">{stats?.average_cgpa ?? '—'}</p>
              </div>
              <BarChart3 className="h-8 w-8 text-purple-600 opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Year-Wise Distribution */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Students Distribution by Year
          </CardTitle>
          <CardDescription>Total enrollment across all years</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            {yearData.map((y) => (
              <div key={y.label} className="p-4 rounded-xl bg-muted/50 text-center">
                <p className="text-sm text-muted-foreground mb-1">{y.label}</p>
                <p className="text-3xl font-bold" style={{ color: y.color }}>{y.count}</p>
                <p className="text-xs text-muted-foreground mt-1">students</p>
              </div>
            ))}
          </div>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={yearData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} />
                <Tooltip formatter={(v) => [`${v} students`]} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]} fill="hsl(var(--primary))" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Fee Collection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              Fee Collection Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Expected</p>
                <p className="text-xl font-bold">{formatCurrency(stats?.fees?.expected ?? 0)}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Collected</p>
                <p className="text-xl font-bold text-emerald-600">{formatCurrency(stats?.fees?.collected ?? 0)}</p>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Collection Progress</span>
                <span className="font-medium">{stats?.fees?.percentage ?? 0}%</span>
              </div>
              <Progress value={stats?.fees?.percentage ?? 0} className="h-2" />
            </div>
            <div className="p-4 rounded-lg bg-muted/50">
              <p className="text-sm text-muted-foreground">Outstanding Balance</p>
              <p className="text-2xl font-bold text-rose-600">{formatCurrency(stats?.fees?.pending ?? 0)}</p>
            </div>
          </CardContent>
        </Card>

        {/* Subject Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Subject Performance
            </CardTitle>
            <CardDescription>Average marks across top 5 subjects</CardDescription>
          </CardHeader>
          <CardContent>
            {performance_trend && performance_trend.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={performance_trend}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="subject" tick={{ fontSize: 10 }} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="average" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-muted-foreground text-sm">
                No marks data available yet
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default DepartmentDetails;
