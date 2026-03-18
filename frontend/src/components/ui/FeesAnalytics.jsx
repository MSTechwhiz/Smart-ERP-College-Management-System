import React, { useState, useEffect } from 'react';
import { DollarSign, TrendingUp, TrendingDown, Users, Building2, Download, PieChart } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './card';
import { Button } from './button';
import { Progress } from './progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './select';
import { feesAnalyticsAPI, departmentAPI } from '../../services/api';
import { toast } from 'sonner';

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount || 0);
};

export function FeesAnalytics() {
  const [analytics, setAnalytics] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [selectedDept, setSelectedDept] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [selectedDept]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [analyticsRes, deptRes] = await Promise.all([
        feesAnalyticsAPI.getAnalytics(null, selectedDept === 'all' ? null : selectedDept),
        departmentAPI.getAll()
      ]);
      setAnalytics(analyticsRes.data);
      setDepartments(deptRes.data);
    } catch (error) {
      toast.error('Failed to load analytics');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleExportPDF = () => {
    // In a real implementation, this would generate a PDF report
    toast.info('PDF export feature coming soon');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        Failed to load analytics data
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Fees Analytics</h2>
          <p className="text-muted-foreground">Financial overview and collection status</p>
        </div>
        <div className="flex items-center gap-4">
          <Select value={selectedDept} onValueChange={setSelectedDept}>
            <SelectTrigger className="w-48" data-testid="dept-filter">
              <SelectValue placeholder="All Departments" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Departments</SelectItem>
              {departments.map(dept => (
                <SelectItem key={dept.id} value={dept.id}>{dept.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={handleExportPDF}>
            <Download className="h-4 w-4 mr-2" />
            Export PDF
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-full bg-blue-100 dark:bg-blue-900/30">
                <DollarSign className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Expected</p>
                <p className="text-2xl font-bold">{formatCurrency(analytics.total_expected)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-full bg-green-100 dark:bg-green-900/30">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Collected</p>
                <p className="text-2xl font-bold text-green-600">{formatCurrency(analytics.total_collected)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-full bg-red-100 dark:bg-red-900/30">
                <TrendingDown className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Pending</p>
                <p className="text-2xl font-bold text-red-600">{formatCurrency(analytics.total_pending)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-full bg-purple-100 dark:bg-purple-900/30">
                <Users className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Students</p>
                <p className="text-2xl font-bold">{analytics.total_students}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Collection Progress */}
      <Card>
        <CardHeader>
          <CardTitle>Collection Progress</CardTitle>
          <CardDescription>Overall fee collection percentage</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Collection Rate</span>
              <span className="text-lg font-bold text-primary">{analytics.collection_percentage}%</span>
            </div>
            <Progress value={analytics.collection_percentage} className="h-4" />
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Collected: {formatCurrency(analytics.total_collected)}</span>
              <span>Target: {formatCurrency(analytics.total_expected)}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Department-wise Collection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              Department-wise Collection
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analytics.department_wise?.map((dept, index) => (
                <div key={dept.department_id || index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{dept.department_name}</span>
                    <span className="text-sm text-muted-foreground">{dept.student_count} students</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <Progress 
                      value={analytics.total_collected > 0 ? (dept.collected / analytics.total_collected * 100) : 0} 
                      className="flex-1 h-2" 
                    />
                    <span className="text-sm font-bold w-24 text-right">{formatCurrency(dept.collected)}</span>
                  </div>
                </div>
              ))}
              {(!analytics.department_wise || analytics.department_wise.length === 0) && (
                <p className="text-center text-muted-foreground py-4">No department data available</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Payment Status Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="h-5 w-5" />
              Payment Status Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analytics.status_breakdown && Object.entries(analytics.status_breakdown).map(([status, count]) => (
                <div key={status} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${
                      status === 'verified' ? 'bg-green-500' :
                      status === 'pending' ? 'bg-yellow-500' :
                      status === 'screenshot_uploaded' ? 'bg-blue-500' :
                      'bg-red-500'
                    }`}></div>
                    <span className="text-sm font-medium capitalize">{status.replace('_', ' ')}</span>
                  </div>
                  <span className="text-lg font-bold">{count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Monthly Collection Trend */}
      <Card>
        <CardHeader>
          <CardTitle>Monthly Collection Trend</CardTitle>
          <CardDescription>Fee collection over the last 12 months</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-end gap-2">
            {analytics.monthly_collection?.map((month, index) => {
              const maxCollection = Math.max(...analytics.monthly_collection.map(m => m.collected)) || 1;
              const heightPercent = (month.collected / maxCollection) * 100;
              
              return (
                <div key={month.month} className="flex-1 flex flex-col items-center gap-2">
                  <div 
                    className="w-full bg-primary/80 rounded-t transition-all hover:bg-primary"
                    style={{ height: `${Math.max(heightPercent, 5)}%` }}
                    title={formatCurrency(month.collected)}
                  ></div>
                  <span className="text-xs text-muted-foreground transform -rotate-45 origin-left">
                    {month.month.slice(5)}
                  </span>
                </div>
              );
            })}
          </div>
          <div className="flex justify-between mt-4 text-xs text-muted-foreground">
            <span>Older</span>
            <span>Recent</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default FeesAnalytics;
