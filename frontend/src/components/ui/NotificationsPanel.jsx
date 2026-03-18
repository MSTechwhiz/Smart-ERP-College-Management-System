import React, { useState, useEffect } from 'react';
import { Bell, Check, CheckCheck, AlertCircle, CreditCard, FileText, MessageSquare, Megaphone } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './card';
import { Button } from './button';
import { Badge } from './badge';
import { notificationAPI } from '../../services/api';
import { toast } from 'sonner';

export function NotificationsPanel({ onClose }) {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, unread

  useEffect(() => {
    loadNotifications();
  }, [filter]);

  const loadNotifications = async () => {
    try {
      const response = await notificationAPI.getMy(filter === 'unread');
      setNotifications(response.data);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkRead = async (notificationId) => {
    try {
      await notificationAPI.markRead(notificationId);
      setNotifications(notifications.map(n => 
        n.id === notificationId ? { ...n, is_read: true } : n
      ));
    } catch (error) {
      toast.error('Failed to mark as read');
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationAPI.markAllRead();
      setNotifications(notifications.map(n => ({ ...n, is_read: true })));
      toast.success('All notifications marked as read');
    } catch (error) {
      toast.error('Failed to mark all as read');
    }
  };

  const getIcon = (type) => {
    const icons = {
      fee_alert: <CreditCard className="h-4 w-4 text-amber-500" />,
      approval: <FileText className="h-4 w-4 text-blue-500" />,
      attendance: <AlertCircle className="h-4 w-4 text-red-500" />,
      announcement: <Megaphone className="h-4 w-4 text-purple-500" />,
      grievance: <MessageSquare className="h-4 w-4 text-green-500" />,
    };
    return icons[type] || <Bell className="h-4 w-4 text-gray-500" />;
  };

  const getPriorityColor = (priority) => {
    const colors = {
      urgent: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
      high: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
      normal: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
      low: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400',
    };
    return colors[priority] || colors.normal;
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <Card className="w-full max-w-md" data-testid="notifications-panel">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Notifications
          {unreadCount > 0 && (
            <Badge variant="destructive" className="text-xs">{unreadCount}</Badge>
          )}
        </CardTitle>
        <div className="flex gap-2">
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={handleMarkAllRead}
            disabled={unreadCount === 0}
          >
            <CheckCheck className="h-4 w-4 mr-1" />
            Read All
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {/* Filter */}
        <div className="flex gap-2 mb-4">
          <Button 
            variant={filter === 'all' ? 'default' : 'outline'} 
            size="sm"
            onClick={() => setFilter('all')}
          >
            All
          </Button>
          <Button 
            variant={filter === 'unread' ? 'default' : 'outline'} 
            size="sm"
            onClick={() => setFilter('unread')}
          >
            Unread
          </Button>
        </div>

        {/* Notifications List */}
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
          </div>
        ) : notifications.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Bell className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No notifications</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {notifications.map((notification) => (
              <div
                key={notification.id}
                className={`p-3 rounded-lg border transition-colors cursor-pointer ${
                  notification.is_read 
                    ? 'bg-background' 
                    : 'bg-primary/5 border-primary/20'
                }`}
                onClick={() => !notification.is_read && handleMarkRead(notification.id)}
              >
                <div className="flex items-start gap-3">
                  <div className="mt-0.5">
                    {getIcon(notification.notification_type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-sm truncate">{notification.title}</h4>
                      {notification.priority && notification.priority !== 'normal' && (
                        <Badge className={`text-xs ${getPriorityColor(notification.priority)}`}>
                          {notification.priority}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {notification.message}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(notification.created_at).toLocaleString()}
                    </p>
                  </div>
                  {!notification.is_read && (
                    <div className="w-2 h-2 rounded-full bg-primary shrink-0 mt-2"></div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Notification Bell with Badge (for header)
export function NotificationBell({ onClick }) {
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const loadUnread = async () => {
      try {
        const response = await notificationAPI.getMy(true);
        setUnreadCount(response.data.length);
      } catch (error) {
        console.error('Failed to load notifications:', error);
      }
    };
    
    loadUnread();
    // Poll every 30 seconds
    const interval = setInterval(loadUnread, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <button
      onClick={onClick}
      className="relative p-2 hover:bg-muted rounded-lg transition-colors"
      data-testid="notification-bell"
    >
      <Bell className="h-5 w-5" />
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 w-5 h-5 bg-destructive text-destructive-foreground text-xs rounded-full flex items-center justify-center">
          {unreadCount > 9 ? '9+' : unreadCount}
        </span>
      )}
    </button>
  );
}

export default NotificationsPanel;
