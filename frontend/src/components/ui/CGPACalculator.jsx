import React, { useState, useEffect } from 'react';
import { Calculator, Plus, Trash2, Save, Printer, Download } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './card';
import { Button } from './button';
import { Input } from './input';
import { Label } from './label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './select';
import { cgpaAPI } from '../../services/api';
import { toast } from 'sonner';

// Anna University Grade Points
const GRADES = [
  { grade: 'O', points: 10, description: 'Outstanding' },
  { grade: 'A+', points: 9, description: 'Excellent' },
  { grade: 'A', points: 8, description: 'Very Good' },
  { grade: 'B+', points: 7, description: 'Good' },
  { grade: 'B', points: 6, description: 'Above Average' },
  { grade: 'C', points: 5, description: 'Average' },
  { grade: 'U', points: 0, description: 'Fail' },
  { grade: 'RA', points: 0, description: 'Re-appear' },
];

export function CGPACalculator() {
  const [entries, setEntries] = useState([
    { id: 1, subject_name: '', credits: 3, grade: 'O' }
  ]);
  const [semester, setSemester] = useState(1);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await cgpaAPI.getHistory();
      setHistory(response.data);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const addEntry = () => {
    setEntries([...entries, { 
      id: Date.now(), 
      subject_name: '', 
      credits: 3, 
      grade: 'O' 
    }]);
  };

  const removeEntry = (id) => {
    if (entries.length > 1) {
      setEntries(entries.filter(e => e.id !== id));
    }
  };

  const updateEntry = (id, field, value) => {
    setEntries(entries.map(e => 
      e.id === id ? { ...e, [field]: value } : e
    ));
  };

  const calculateSGPA = async (save = false) => {
    if (entries.some(e => !e.subject_name.trim())) {
      toast.error('Please fill all subject names');
      return;
    }

    setLoading(true);
    try {
      const response = await cgpaAPI.calculate(
        entries.map(e => ({
          subject_name: e.subject_name,
          credits: parseInt(e.credits),
          grade: e.grade
        })),
        semester,
        save
      );
      setResult(response.data);
      if (save) {
        toast.success('CGPA saved successfully');
        loadHistory();
      }
    } catch (error) {
      toast.error('Failed to calculate CGPA');
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const getGradeColor = (grade) => {
    const colors = {
      'O': 'text-emerald-600',
      'A+': 'text-green-600',
      'A': 'text-blue-600',
      'B+': 'text-cyan-600',
      'B': 'text-yellow-600',
      'C': 'text-orange-600',
      'U': 'text-red-600',
      'RA': 'text-red-600',
    };
    return colors[grade] || 'text-gray-600';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Calculator className="h-8 w-8 text-primary" />
          <div>
            <h2 className="text-2xl font-bold">CGPA Calculator</h2>
            <p className="text-sm text-muted-foreground">Anna University Grading System</p>
          </div>
        </div>
        <Button 
          variant="outline" 
          onClick={() => setShowHistory(!showHistory)}
        >
          {showHistory ? 'Hide History' : 'View History'}
        </Button>
      </div>

      {/* Grade Reference */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Grade Points Reference</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            {GRADES.map(g => (
              <div key={g.grade} className="flex items-center gap-2 text-sm">
                <span className={`font-bold ${getGradeColor(g.grade)}`}>{g.grade}</span>
                <span className="text-muted-foreground">= {g.points}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calculator Form */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Enter Subjects</CardTitle>
              <CardDescription>Add your subjects with credits and grades</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Semester Selection */}
              <div className="flex items-center gap-4">
                <Label>Semester</Label>
                <Select value={String(semester)} onValueChange={(v) => setSemester(parseInt(v))}>
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[1,2,3,4,5,6,7,8].map(s => (
                      <SelectItem key={s} value={String(s)}>Semester {s}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Subject Entries */}
              <div className="space-y-3">
                {entries.map((entry, index) => (
                  <div key={entry.id} className="flex items-center gap-3 p-3 rounded-lg bg-muted/30">
                    <span className="text-sm text-muted-foreground w-6">{index + 1}.</span>
                    <Input
                      placeholder="Subject Name"
                      value={entry.subject_name}
                      onChange={(e) => updateEntry(entry.id, 'subject_name', e.target.value)}
                      className="flex-1"
                      data-testid={`subject-name-${index}`}
                    />
                    <Select 
                      value={String(entry.credits)} 
                      onValueChange={(v) => updateEntry(entry.id, 'credits', parseInt(v))}
                    >
                      <SelectTrigger className="w-24" data-testid={`credits-${index}`}>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {[1,2,3,4,5,6].map(c => (
                          <SelectItem key={c} value={String(c)}>{c} Credit{c > 1 ? 's' : ''}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Select 
                      value={entry.grade} 
                      onValueChange={(v) => updateEntry(entry.id, 'grade', v)}
                    >
                      <SelectTrigger className="w-24" data-testid={`grade-${index}`}>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {GRADES.map(g => (
                          <SelectItem key={g.grade} value={g.grade}>
                            <span className={getGradeColor(g.grade)}>{g.grade}</span>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => removeEntry(entry.id)}
                      disabled={entries.length === 1}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                ))}
              </div>

              <Button variant="outline" onClick={addEntry} className="w-full">
                <Plus className="h-4 w-4 mr-2" />
                Add Subject
              </Button>

              <div className="flex gap-3 pt-4">
                <Button onClick={() => calculateSGPA(false)} disabled={loading} className="flex-1">
                  Calculate SGPA
                </Button>
                <Button onClick={() => calculateSGPA(true)} disabled={loading} variant="outline">
                  <Save className="h-4 w-4 mr-2" />
                  Save
                </Button>
                <Button variant="outline" onClick={handlePrint}>
                  <Printer className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Result */}
        <div className="space-y-4">
          {result && (
            <Card className="border-primary">
              <CardHeader className="pb-2">
                <CardTitle>Result</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-4">
                  <div className="text-5xl font-bold text-primary mb-2">
                    {result.sgpa.toFixed(2)}
                  </div>
                  <p className="text-muted-foreground">SGPA</p>
                </div>
                <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                  <div className="text-center">
                    <p className="text-2xl font-bold">{result.total_credits}</p>
                    <p className="text-xs text-muted-foreground">Total Credits</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold">{result.weighted_sum}</p>
                    <p className="text-xs text-muted-foreground">Weighted Sum</p>
                  </div>
                </div>
                {result.saved && (
                  <p className="text-center text-sm text-green-600 mt-4">Saved to your profile</p>
                )}
              </CardContent>
            </Card>
          )}

          {/* History */}
          {showHistory && history.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Saved Calculations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {history.map((calc, index) => (
                    <div key={calc.id || index} className="flex items-center justify-between p-2 rounded bg-muted/30">
                      <div>
                        <p className="text-sm font-medium">Semester {calc.semester || '-'}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(calc.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-primary">{calc.sgpa?.toFixed(2)}</p>
                        <p className="text-xs text-muted-foreground">{calc.total_credits} credits</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

export default CGPACalculator;
