import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  GraduationCap, 
  Users, 
  Building2, 
  UserCog, 
  Crown,
  ArrowRight,
  BookOpen,
  Shield,
  Sparkles,
  Bell,
  Clock,
  ChevronRight,
  Newspaper,
  Calendar,
  AlertTriangle
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { useAuth } from '../context/AuthContext';
import { seedAPI } from '../services/api';
import { toast } from 'sonner';

const roles = [
  {
    id: 'principal',
    title: 'Principal',
    description: 'Institution governance & oversight',
    icon: Crown,
    color: 'bg-amber-100 text-amber-600',
    borderColor: 'border-amber-200 hover:shadow-amber-500/10',
    gridArea: 'col-span-1'
  },
  {
    id: 'admin',
    title: 'Admin / Office',
    description: 'Records, admissions & finance',
    icon: Building2,
    color: 'bg-blue-100 text-blue-600',
    borderColor: 'border-blue-200 hover:shadow-blue-500/10',
    gridArea: 'col-span-1'
  },
  {
    id: 'hod',
    title: 'HOD',
    description: 'Department governance',
    icon: UserCog,
    color: 'bg-purple-100 text-purple-600',
    borderColor: 'border-purple-200 hover:border-purple-400',
    gridArea: 'col-span-1'
  },
  {
    id: 'faculty',
    title: 'Faculty',
    description: 'Academic operations',
    icon: Users,
    color: 'bg-emerald-100 text-emerald-600',
    borderColor: 'border-emerald-200 hover:shadow-emerald-500/10',
    gridArea: 'col-span-1'
  },
  {
    id: 'student',
    title: 'Student',
    description: 'Academic portal access',
    icon: GraduationCap,
    color: 'bg-rose-100 text-rose-600',
    borderColor: 'border-rose-200 hover:shadow-rose-500/10',
    gridArea: 'col-span-1 sm:col-span-2 place-self-center w-full sm:w-1/2'
  },
];

import { liveUpdatesService } from '../services/liveUpdatesService';

// Fallback announcements in case of service issues or initial load
const initialAnnouncements = [
  { id: 1, title: 'Anna University Results Published', date: 'Today', icon: Newspaper, color: 'text-blue-600', type: 'University' },
  { id: 2, title: 'Revaluation Dates Announced', date: 'Yesterday', icon: Calendar, color: 'text-emerald-600', type: 'University' },
  { id: 3, title: 'Exam Timetable Released', date: '2 days ago', icon: Clock, color: 'text-amber-600', type: 'College' },
  { id: 4, title: 'College Circular Updates', date: '3 days ago', icon: Bell, color: 'text-purple-600', type: 'College' },
];

const NewsTicker = () => (
  <div className="bg-white/80 backdrop-blur-md text-slate-900 py-2 overflow-hidden border-b border-slate-200 relative z-50">
    <div className="flex items-center whitespace-nowrap animate-marquee font-semibold text-sm">
      <span className="mx-8 flex items-center gap-2 text-slate-800"><AlertTriangle className="h-4 w-4 text-amber-600" /> 🚨 Anna University Results Out</span>
      <span className="mx-8 flex items-center gap-2 text-slate-800"><Bell className="h-4 w-4 text-blue-600" /> 📢 Internal Exams from March 25</span>
      <span className="mx-8 flex items-center gap-2 text-slate-800"><Sparkles className="h-4 w-4 text-emerald-600" /> 🔔 Fee Deadline Reminder</span>
      <span className="mx-8 flex items-center gap-2 text-slate-800"><AlertTriangle className="h-4 w-4 text-amber-600" /> 🚨 Anna University Results Out</span>
      <span className="mx-8 flex items-center gap-2 text-slate-800"><Bell className="h-4 w-4 text-blue-600" /> 📢 Internal Exams from March 25</span>
      <span className="mx-8 flex items-center gap-2 text-slate-800"><Sparkles className="h-4 w-4 text-emerald-600" /> 🔔 Fee Deadline Reminder</span>
    </div>
  </div>
);

export default function LandingPage() {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  const [seeding, setSeeding] = useState(false);
  const [greeting, setGreeting] = useState('');
  const [lastUpdated, setLastUpdated] = useState('2 mins ago');
  const [activeAnnIdx, setActiveAnnIdx] = useState(0);
  const [announcements, setAnnouncements] = useState(initialAnnouncements);

  const fetchUpdates = async () => {
    try {
      const liveData = await liveUpdatesService.fetchLiveUpdates();
      if (liveData && liveData.length > 0) {
        setAnnouncements(liveData);
        setLastUpdated('Just now');
      }
    } catch (error) {
      console.warn('Live updates failed, using fallback');
    }
  };

  useEffect(() => {
    if (isAuthenticated && user) {
      navigate(`/${user.role}`);
    }
    
    // Set dynamic greeting
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good Morning');
    else if (hour < 17) setGreeting('Good Afternoon');
    else setGreeting('Good Evening');

    // Initial fetch
    fetchUpdates();

    // Auto-rotate announcements
    const rotateInterval = setInterval(() => {
      setActiveAnnIdx((prev) => (prev + 1) % announcements.length);
    }, 4000);

    // Auto-refresh updates feed (60 seconds)
    const refreshInterval = setInterval(() => {
      fetchUpdates();
    }, 60000);

    // Update timestamp simulation
    const timeInterval = setInterval(() => {
      setLastUpdated((prev) => prev === 'Just now' ? '1 min ago' : prev);
    }, 60000);

    return () => {
      clearInterval(rotateInterval);
      clearInterval(refreshInterval);
      clearInterval(timeInterval);
    };
  }, [isAuthenticated, user, navigate, announcements.length]);

  const handleRoleSelect = (roleId) => {
    navigate(`/login/${roleId}`);
  };

  const handleSeedData = async () => {
    setSeeding(true);
    try {
      const response = await seedAPI.seed();
      if (response.data.status === 'already_seeded') {
        toast.info('Demo data already exists');
      } else {
        toast.success('Demo data seeded successfully!');
      }
    } catch (error) {
      toast.error('Failed to seed data');
    } finally {
      setSeeding(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col font-sans selection:bg-amber-500/30 overflow-x-hidden bg-transparent main-container">
      <NewsTicker />

      {/* Main Container - Fully Translucent Wrapper */}
      <div className="flex-1 relative flex flex-col lg:flex-row overflow-hidden bg-transparent">
        
        {/* Left Side: Live Updates (50%) */}
        <div className="relative z-10 w-full lg:w-1/2 flex flex-col justify-center px-8 lg:px-16 py-12 lg:py-0 bg-gradient-to-r from-white/80 to-transparent">
          <div className="animate-fade-in space-y-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-12 w-12 rounded-2xl bg-amber-500 flex items-center justify-center shadow-lg shadow-amber-500/20 rotate-3">
                <GraduationCap className="h-7 w-7 text-white" />
              </div>
              <h1 className="text-3xl font-black tracking-tighter sm:text-4xl italic text-slate-900">ACADEMIA<span className="text-amber-600">OS</span></h1>
            </div>

            <div className="space-y-2">
              <h2 className="text-4xl sm:text-5xl font-bold tracking-tight text-slate-900">
                {greeting},
                <span className="block text-amber-600 drop-shadow-sm">Welcome back.</span>
              </h2>
              <p className="text-lg text-slate-600 max-w-md leading-relaxed font-medium">
                Empowering institutional excellence through intelligent automation and collaborative governance.
              </p>
            </div>

            {/* Campus Live Updates Section - Light Glass */}
            <div className="bg-white/85 backdrop-blur-[6px] border border-white rounded-3xl p-6 sm:p-8 max-w-md shadow-xl relative overflow-hidden group border-opacity-50">
              <div className="absolute top-0 right-0 p-4">
                <Sparkles className="h-5 w-5 text-amber-600 animate-pulse" />
              </div>
              
              <h3 className="text-sm font-bold uppercase tracking-widest text-amber-600 mb-6 flex items-center gap-2">
                <Newspaper className="h-4 w-4" /> Campus Live Updates
              </h3>

              <div className="space-y-6">
                {announcements.map((ann, idx) => (
                  <div 
                    key={ann.id}
                    className={`transition-all duration-500 flex items-start gap-4 ${
                      idx === activeAnnIdx ? 'opacity-100 translate-x-0' : 'opacity-0 absolute translate-x-4 pointer-events-none'
                    }`}
                  >
                    <div className={`p-3 rounded-2xl bg-white/50 ${ann.color} shadow-sm border border-slate-100/50`}>
                      <ann.icon className="h-6 w-6" />
                    </div>
                    <div>
                      <h4 className="font-bold text-lg leading-tight mb-1 text-slate-900">{ann.title}</h4>
                      <div className="flex items-center gap-2 text-xs text-slate-500 font-bold">
                        <Clock className="h-3 w-3" />
                        <span>{ann.date}</span>
                        {ann.type && (
                          <span className={`ml-2 px-1.5 py-0.5 rounded-md text-[9px] uppercase tracking-tighter ${
                            ann.type === 'University' ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' : 'bg-blue-50 text-blue-600 border border-blue-100'
                          }`}>
                            {ann.type}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8 pt-6 border-t border-slate-200 flex items-center justify-between">
                <span className="text-[10px] font-black uppercase tracking-tighter text-slate-400">STATUS: ACTIVE</span>
                <span className="text-[10px] font-black uppercase tracking-tighter text-slate-400">Refreshed: {lastUpdated}</span>
              </div>
            </div>

            <div className="flex items-center gap-6 text-slate-500">
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-emerald-600" />
                <span className="text-xs font-bold uppercase tracking-wider">Secured Access</span>
              </div>
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-amber-600" />
                <span className="text-xs font-bold uppercase tracking-wider">v2.0 Premium</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side: Role Selection (50%) */}
        <div className="relative z-10 w-full lg:w-1/2 flex items-center justify-center px-8 lg:px-16 py-12 bg-transparent">
          <div className="w-full max-w-xl">
            <h2 className="text-center text-xs font-black text-amber-600 uppercase tracking-[0.3em] mb-10 opacity-90">
              System Gateway / Role Selection
            </h2>

            <div className="grid grid-cols-2 gap-4 sm:gap-6">
              {roles.map((role) => (
                <div 
                  key={role.id}
                  className={`${role.gridArea} group cursor-pointer`}
                  onClick={() => handleRoleSelect(role.id)}
                >
                  <Card 
                    className={`h-full border border-white bg-white/85 backdrop-blur-[6px] overflow-hidden transition-all duration-300 hover:border-amber-500/50 hover:bg-white hover:-translate-y-1 hover:shadow-2xl hover:shadow-amber-500/10 rounded-[2rem] shadow-soft`}
                  >
                    <CardContent className="p-6 sm:p-8 flex flex-col h-full relative">
                      <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity translate-x-4 group-hover:translate-x-0 duration-300">
                        <ArrowRight className="h-5 w-5 text-amber-600" />
                      </div>

                      <div className={`w-12 h-12 rounded-2xl ${role.color} flex items-center justify-center mb-6 transition-transform group-hover:scale-110 duration-300 shadow-inner`}>
                        <role.icon className="h-6 w-6" />
                      </div>

                      <div>
                        <h3 className="text-xl font-bold mb-2 group-hover:text-amber-600 transition-colors text-slate-900">
                          {role.title}
                        </h3>
                        <p className="text-sm text-slate-500 leading-snug font-medium">
                          {role.description}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ))}
            </div>

            <div className="mt-12 flex justify-center">
              <Button 
                variant="ghost" 
                className="text-slate-500 hover:text-slate-900 hover:bg-white/60 rounded-full px-6 transition-all border border-transparent hover:border-slate-200"
                onClick={handleSeedData}
                disabled={seeding}
              >
                {seeding ? (
                  <span className="flex items-center gap-2">
                    <div className="h-3 w-3 animate-spin rounded-full border-2 border-slate-400 border-t-amber-600"></div>
                    Waking Systems...
                  </span>
                ) : 'Recalibrate Demo Systems'}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
