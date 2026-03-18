import React, { useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { 
  GraduationCap, 
  ArrowLeft, 
  Mail, 
  Lock,
  Eye,
  EyeOff,
  Loader2,
  Crown,
  Building2,
  UserCog,
  Users
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

const roleConfig = {
  principal: {
    title: 'Principal',
    description: 'Institution governance dashboard',
    icon: Crown,
    color: 'bg-amber-500',
    gradient: 'from-amber-500 to-orange-600',
  },
  admin: {
    title: 'Admin / Office',
    description: 'Records and finance management',
    icon: Building2,
    color: 'bg-blue-500',
    gradient: 'from-blue-500 to-indigo-600',
  },
  hod: {
    title: 'Head of Department',
    description: 'Department control center',
    icon: UserCog,
    color: 'bg-purple-500',
    gradient: 'from-purple-500 to-violet-600',
  },
  faculty: {
    title: 'Faculty',
    description: 'Academic operations panel',
    icon: Users,
    color: 'bg-emerald-500',
    gradient: 'from-emerald-500 to-teal-600',
  },
  student: {
    title: 'Student',
    description: 'Personal academic portal',
    icon: GraduationCap,
    color: 'bg-rose-500',
    gradient: 'from-rose-500 to-pink-600',
  },
};

export default function LoginPage() {
  const { role } = useParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const config = roleConfig[role] || roleConfig.student;
  const IconComponent = config.icon;

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast.error('Please fill in all fields');
      return;
    }

    setLoading(true);
    
    try {
      const result = await login(email, password, role);
      
      if (result.success) {
        toast.success('Login successful!', {
          description: `Welcome back, ${result.user.name}`,
        });
        
        const userRole = result.user.role;
        console.log('Login response:', result);
        console.log('Redirecting role:', userRole);
        
        // Role-based redirect
        if (userRole === 'faculty' && result.user.department_code) {
          navigate(`/faculty/${result.user.department_code.toLowerCase()}`);
        } else if (userRole === 'student') {
          navigate('/student');
        } else if (userRole === 'admin') {
          navigate('/admin');
        } else if (userRole === 'principal') {
          navigate('/principal');
        } else if (userRole === 'hod') {
          navigate('/hod');
        } else {
          navigate(`/${userRole}`);
        }
      } else {
        toast.error('Login failed', {
          description: result.error,
        });
      }
    } catch (error) {
      toast.error('An error occurred during login');
    } finally {
      setLoading(false);
    }
  };

  // Demo credentials helper
  const demoCredentials = {
    principal: { email: 'principal@academia.edu', password: 'principal123' },
    admin: { email: 'admin@academia.edu', password: 'admin123' },
    hod: { email: 'hod.cse@academia.edu', password: 'hod123' },
    faculty: { email: 'faculty@academia.edu', password: 'faculty123' },
    student: { email: 'student@academia.edu', password: 'student123' },
  };

  const fillDemoCredentials = () => {
    const creds = demoCredentials[role];
    if (creds) {
      setEmail(creds.email);
      setPassword(creds.password);
      toast.info('Demo credentials filled');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex">
      {/* Left Panel - Decorative */}
      <div className={`hidden lg:flex lg:w-1/2 bg-gradient-to-br ${config.gradient} relative overflow-hidden`}>
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJNMzYgMzRjMC0yLjIxLTEuNzktNC00LTRzLTQgMS43OS00IDQgMS43OSA0IDQgNCAzLjk5LTEuNzkgNC00eiIvPjwvZz48L2c+PC9zdmc+')] opacity-30"></div>
        
        <div className="relative z-10 flex flex-col justify-center items-center w-full p-12 text-white">
          <div className="p-6 rounded-3xl bg-white/10 backdrop-blur-sm mb-8">
            <IconComponent className="h-16 w-16" />
          </div>
          <h2 className="text-3xl font-bold mb-4 text-center">{config.title} Portal</h2>
          <p className="text-lg opacity-90 text-center max-w-md">{config.description}</p>
          
          <div className="mt-12 space-y-4 text-center">
            <p className="text-sm opacity-75">Secure role-based access control</p>
            <div className="flex items-center gap-2 justify-center">
              <div className="h-2 w-2 rounded-full bg-white animate-pulse"></div>
              <span className="text-sm">Real-time updates enabled</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          {/* Back Link */}
          <Link 
            to="/" 
            className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-8 transition-colors"
            data-testid="back-to-home"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to role selection
          </Link>

          {/* Mobile Role Badge */}
          <div className="lg:hidden flex items-center gap-3 mb-6">
            <div className={`p-2 rounded-lg ${config.color}`}>
              <IconComponent className="h-5 w-5 text-white" />
            </div>
            <span className="font-semibold">{config.title} Login</span>
          </div>

          <Card className="border-0 shadow-xl">
            <CardHeader className="space-y-1">
              <div className="flex items-center gap-2 mb-2">
                <GraduationCap className="h-6 w-6 text-amber-600" />
                <span className="font-bold">AcademiaOS</span>
              </div>
              <CardTitle className="text-2xl">Welcome back</CardTitle>
              <CardDescription>
                Enter your credentials to access your dashboard
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="name@institution.edu"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-10"
                      data-testid="login-email-input"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-10 pr-10"
                      data-testid="login-password-input"
                    />
                    <button
                      type="button"
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                      onClick={() => setShowPassword(!showPassword)}
                      tabIndex={-1}
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                    >
                      {showPassword
                        ? <EyeOff className="h-4 w-4" />
                        : <Eye className="h-4 w-4" />
                      }
                    </button>
                  </div>
                </div>

                <Button 
                  type="submit" 
                  className="w-full" 
                  disabled={loading}
                  data-testid="login-submit-btn"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Signing in...
                    </>
                  ) : (
                    'Sign In'
                  )}
                </Button>

                <Button 
                  type="button"
                  variant="outline" 
                  className="w-full"
                  onClick={fillDemoCredentials}
                  data-testid="fill-demo-btn"
                >
                  Fill Demo Credentials
                </Button>
              </form>
            </CardContent>
          </Card>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            First time? Click "Load Demo Data" on the home page to create test accounts.
          </p>
        </div>
      </div>
    </div>
  );
}
