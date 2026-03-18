import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bell,
  Trash2,
  CheckCircle2,
  ArrowLeft,
  Filter,
  Megaphone,
  GraduationCap,
  Settings,
  ShieldAlert
} from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { notificationAPI } from '../../services/api';
import { toast } from 'sonner';
import { formatDateTime } from '../../lib/utils';

export default function AlertsPage() {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await notificationAPI.getMy();
      setNotifications(response.data);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (id) => {
    try {
      await notificationAPI.markRead(id);
      setNotifications(notifications.map(n => 
        n.id === id ? { ...n, is_read: true } : n
      ));
    } catch (error) {
      toast.error('Failed to mark as read');
    }
  };

  const markAllRead = async () => {
    try {
      await notificationAPI.markAllRead();
      setNotifications(notifications.map(n => ({ ...n, is_read: true })));
      toast.success('All notifications marked as read');
    } catch (error) {
      toast.error('Failed to mark all as read');
    }
  };

  const deleteNotification = async (id) => {
    try {
      await notificationAPI.delete(id);
      setNotifications(notifications.filter(n => n.id !== id));
      toast.success('Notification deleted');
    } catch (error) {
      toast.error('Failed to delete notification');
    }
  };

  const getTypeIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'announcement': return <Megaphone className="h-4 w-4" />;
      case 'academic': return <GraduationCap className="h-4 w-4" />;
      case 'administrative': return <ShieldAlert className="h-4 w-4" />;
      default: return <Settings className="h-4 w-4" />;
    }
  };

  const filteredNotifications = notifications.filter(n => {
    if (activeTab === 'all') return true;
    return n.type?.toLowerCase() === activeTab.toLowerCase();
  });

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-4 sm:p-6 lg:p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Bell className="h-6 w-6 text-primary" />
              Notifications
            </h1>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={markAllRead} disabled={!notifications.some(n => !n.is_read)}>
              <CheckCircle2 className="h-4 w-4 mr-2" />
              Mark all read
            </Button>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid grid-cols-5 w-full max-w-2xl">
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="Announcement">Announcements</TabsTrigger>
            <TabsTrigger value="Academic">Academic</TabsTrigger>
            <TabsTrigger value="Administrative">Admin</TabsTrigger>
            <TabsTrigger value="System">System</TabsTrigger>
          </TabsList>
        </Tabs>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg font-medium flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              {activeTab === 'all' ? 'Recent Alerts' : `${activeTab} Notifications`}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex flex-col items-center justify-center py-12 gap-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <p className="text-sm text-muted-foreground">Loading your alerts...</p>
              </div>
            ) : filteredNotifications.length === 0 ? (
              <div className="text-center py-12 space-y-3">
                <Bell className="h-12 w-12 mx-auto text-muted-foreground opacity-20" />
                <p className="text-muted-foreground">No notifications found</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredNotifications.map((n) => (
                  <div 
                    key={n.id} 
                    className={`group relative flex items-start gap-4 p-4 rounded-xl border transition-all ${
                      n.is_read 
                        ? 'bg-background hover:bg-muted/30' 
                        : 'bg-primary/5 border-primary/20 shadow-sm'
                    }`}
                  >
                    <div className={`mt-1 p-2 rounded-lg ${
                      n.is_read ? 'bg-muted text-muted-foreground' : 'bg-primary/10 text-primary'
                    }`}>
                      {getTypeIcon(n.type)}
                    </div>
                    <div className="flex-1 min-w-0 pr-12">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className={`font-semibold text-sm truncate ${n.is_read ? '' : 'text-primary'}`}>
                          {n.title}
                        </h3>
                        {!n.is_read && (
                          <span className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                        )}
                        <Badge variant="outline" className="text-[10px] h-4 px-1 capitalize">
                          {n.type}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground leading-relaxed mb-2">
                        {n.message}
                      </p>
                      <p className="text-[10px] text-muted-foreground font-medium">
                        {formatDateTime(n.created_at)}
                      </p>
                    </div>
                    <div className="absolute top-4 right-4 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      {!n.is_read && (
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          className="h-8 w-8 text-primary hover:bg-primary/10"
                          onClick={() => markAsRead(n.id)}
                          title="Mark as read"
                        >
                          <CheckCircle2 className="h-4 w-4" />
                        </Button>
                      )}
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="h-8 w-8 text-destructive hover:bg-destructive/10"
                        onClick={() => deleteNotification(n.id)}
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
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
