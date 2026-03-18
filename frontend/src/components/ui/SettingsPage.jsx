import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './card';
import { Button } from './button';
import { Input } from './input';
import { Label } from './label';
import { Badge } from './badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './select';
import { Switch } from './switch';
import { settingsAPI } from '../../services/api';
import { toast } from 'sonner';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { Sun, Moon, Monitor, Lock, Bell, Palette, User, Shield, Building2 } from 'lucide-react';

// Settings Page Component
export function SettingsPage() {
  const { user, logout } = useAuth();
  const { themeMode, setThemeMode, colorScheme, setColorScheme } = useTheme();
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [passwords, setPasswords] = useState({
    current: '',
    new: '',
    confirm: ''
  });
  const [changingPassword, setChangingPassword] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await settingsAPI.get();
      setSettings(response.data);
    } catch (error) {
      console.error('Error loading settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateSetting = async (key, value) => {
    try {
      if (key === 'theme') {
        setThemeMode(value);
      }
      if (key === 'color_scheme') {
        setColorScheme(value);
      }
      await settingsAPI.update({ [key]: value });
      setSettings({ ...settings, [key]: value });
      toast.success('Settings updated');
    } catch (error) {
      toast.error('Failed to update settings');
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();

    if (passwords.new !== passwords.confirm) {
      toast.error('New passwords do not match');
      return;
    }

    if (passwords.new.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    setChangingPassword(true);
    try {
      await settingsAPI.changePassword({
        current_password: passwords.current,
        new_password: passwords.new
      });
      toast.success('Password changed successfully');
      setPasswords({ current: '', new: '', confirm: '' });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setChangingPassword(false);
    }
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
      <h2 className="text-2xl font-bold">Settings</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Appearance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Palette className="h-5 w-5" />
              Appearance
            </CardTitle>
            <CardDescription>Customize the look and feel</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>Theme Mode</Label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {[
                  { value: 'light', icon: Sun, label: 'Light' },
                  { value: 'dark', icon: Moon, label: 'Dark' },
                  { value: 'system', icon: Monitor, label: 'System' },
                  { value: 'institutional', icon: Building2, label: 'Institutional' },
                ].map(({ value, icon: Icon, label }) => (
                  <Button
                    key={value}
                    variant={themeMode === value ? 'default' : 'outline'}
                    className="flex-1"
                    onClick={() => handleUpdateSetting('theme', value)}
                    data-testid={`theme-${value}`}
                  >
                    <Icon className="h-4 w-4 mr-2" />
                    {label}
                  </Button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <Label>Color Scheme</Label>
              <div className="flex gap-2 flex-wrap">
                {[
                  { name: 'blue', color: '#3b82f6' },
                  { name: 'green', color: '#22c55e' },
                  { name: 'purple', color: '#a855f7' },
                  { name: 'orange', color: '#f97316' },
                  { name: 'red', color: '#ef4444' },
                  { name: 'slate', color: '#64748b' }
                ].map((scheme) => (
                  <Button
                    key={scheme.name}
                    variant={colorScheme === scheme.name ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleUpdateSetting('color_scheme', scheme.name)}
                    className="capitalize"
                    data-testid={`color-${scheme.name}`}
                  >
                    <div
                      className={`w-4 h-4 rounded-full mr-2`}
                      style={{ backgroundColor: scheme.color }}
                    />
                    {scheme.name}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Notifications
            </CardTitle>
            <CardDescription>Manage your notification preferences</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Email Notifications</p>
                <p className="text-sm text-muted-foreground">
                  Receive updates via email
                </p>
              </div>
              <Switch
                checked={settings?.notification_email ?? true}
                onCheckedChange={(checked) => handleUpdateSetting('notification_email', checked)}
                data-testid="notification-email"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Push Notifications</p>
                <p className="text-sm text-muted-foreground">
                  Receive browser push notifications
                </p>
              </div>
              <Switch
                checked={settings?.notification_push ?? true}
                onCheckedChange={(checked) => handleUpdateSetting('notification_push', checked)}
                data-testid="notification-push"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">SMS Notifications</p>
                <p className="text-sm text-muted-foreground">
                  Receive important alerts via SMS
                </p>
              </div>
              <Switch
                checked={settings?.notification_sms ?? false}
                onCheckedChange={(checked) => handleUpdateSetting('notification_sms', checked)}
                data-testid="notification-sms"
              />
            </div>
          </CardContent>
        </Card>

        {/* Security */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lock className="h-5 w-5" />
              Security
            </CardTitle>
            <CardDescription>Change your password</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleChangePassword} className="space-y-4">
              <div className="space-y-2">
                <Label>Current Password</Label>
                <Input
                  type="password"
                  value={passwords.current}
                  onChange={(e) => setPasswords({ ...passwords, current: e.target.value })}
                  placeholder="Enter current password"
                  required
                  data-testid="current-password"
                />
              </div>
              <div className="space-y-2">
                <Label>New Password</Label>
                <Input
                  type="password"
                  value={passwords.new}
                  onChange={(e) => setPasswords({ ...passwords, new: e.target.value })}
                  placeholder="Enter new password"
                  required
                  data-testid="new-password"
                />
              </div>
              <div className="space-y-2">
                <Label>Confirm New Password</Label>
                <Input
                  type="password"
                  value={passwords.confirm}
                  onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })}
                  placeholder="Confirm new password"
                  required
                  data-testid="confirm-password"
                />
              </div>
              <Button
                type="submit"
                className="w-full"
                disabled={changingPassword}
                data-testid="change-password-btn"
              >
                {changingPassword ? 'Changing...' : 'Change Password'}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Account Info */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Account
            </CardTitle>
            <CardDescription>Your account information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
              <span className="text-muted-foreground">Name</span>
              <span className="font-medium">{user?.name}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
              <span className="text-muted-foreground">Email</span>
              <span className="font-medium">{user?.email}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
              <span className="text-muted-foreground">Role</span>
              <Badge className="capitalize">{user?.role}</Badge>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
              <span className="text-muted-foreground">Language</span>
              <Select
                value={settings?.language || 'en'}
                onValueChange={(value) => handleUpdateSetting('language', value)}
              >
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="hi">Hindi</SelectItem>
                  <SelectItem value="ta">Tamil</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              variant="destructive"
              className="w-full mt-4"
              onClick={logout}
              data-testid="logout-btn"
            >
              Logout
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Profile Page Component (View-Only)
export function ProfilePage({ profile, loading }) {
  const { user } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">My Profile</h2>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
              <User className="h-8 w-8 text-primary" />
            </div>
            <div>
              <h3 className="text-xl font-semibold">{user?.name}</h3>
              <p className="text-muted-foreground">{user?.email}</p>
              <Badge className="mt-1 capitalize">{user?.role}</Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {profile && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(profile).map(([key, value]) => {
                // Skip certain fields
                if (['id', 'user_id', 'password', '_id'].includes(key) || value === null || value === undefined) {
                  return null;
                }

                // Format the key for display
                const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

                // Format the value
                let displayValue = value;
                if (typeof value === 'object') {
                  displayValue = JSON.stringify(value);
                } else if (typeof value === 'boolean') {
                  displayValue = value ? 'Yes' : 'No';
                }

                return (
                  <div key={key} className="p-3 rounded-lg bg-muted/50">
                    <Label className="text-muted-foreground text-xs uppercase tracking-wide">{label}</Label>
                    <p className="font-medium mt-1">{displayValue}</p>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default SettingsPage;
