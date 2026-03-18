import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Inbox,
  Send,
  FileEdit,
  Archive,
  ArrowLeft,
  Star,
  RefreshCw,
  Plus,
  Search,
  Mail as MailIcon
} from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
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
  DialogTrigger,
} from '../../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { mailAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { toast } from 'sonner';
import { formatDateTime } from '../../lib/utils';

export default function MailboxPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('inbox');
  const [inbox, setInbox] = useState([]);
  const [sent, setSent] = useState([]);
  const [drafts, setDrafts] = useState([]);
  const [recipients, setRecipients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [composeOpen, setComposeOpen] = useState(false);
  const [selectedMail, setSelectedMail] = useState(null);
  const [composeData, setComposeData] = useState({
    to_user_id: '',
    subject: '',
    body: '',
    priority: 'normal'
  });

  useEffect(() => {
    loadMailData();
  }, []);

  const loadMailData = async () => {
    setLoading(true);
    try {
      const [inboxRes, sentRes, draftsRes, recipientsRes] = await Promise.all([
        mailAPI.getInbox(),
        mailAPI.getSent(),
        mailAPI.getDrafts(),
        mailAPI.getRecipients()
      ]);
      setInbox(inboxRes.data);
      setSent(sentRes.data);
      setDrafts(draftsRes.data);
      setRecipients(recipientsRes.data);
    } catch (error) {
      console.error('Error loading mail:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async () => {
    if (!composeData.to_user_id || !composeData.subject || !composeData.body) {
      toast.error('Please fill all fields');
      return;
    }

    try {
      await mailAPI.send(composeData);
      toast.success('Mail sent successfully');
      setComposeOpen(false);
      setComposeData({ to_user_id: '', subject: '', body: '', priority: 'normal' });
      loadMailData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send mail');
    }
  };

  const handleSaveDraft = async () => {
    try {
      await mailAPI.send({ ...composeData, is_draft: true });
      toast.success('Draft saved');
      setComposeOpen(false);
      loadMailData();
    } catch (error) {
      toast.error('Failed to save draft');
    }
  };

  const handleMarkRead = async (mailId) => {
    try {
      await mailAPI.markRead(mailId);
      loadMailData();
    } catch (error) {
      console.error('Error marking read:', error);
    }
  };

  const handleSelectMail = (mail) => {
    setSelectedMail(mail);
    if (!mail.is_read && activeTab === 'inbox') {
      handleMarkRead(mail.id);
    }
  };

  const MailList = ({ mails, showFrom = true }) => (
    <div className="space-y-2">
      {mails.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          <MailIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No messages</p>
        </div>
      ) : (
        mails.map((mail) => (
          <div
            key={mail.id}
            className={`p-4 rounded-lg border cursor-pointer transition-colors ${
              selectedMail?.id === mail.id 
                ? 'bg-primary/5 border-primary' 
                : mail.is_read 
                  ? 'hover:bg-muted/50' 
                  : 'bg-blue-50 dark:bg-blue-950/20 hover:bg-blue-100 dark:hover:bg-blue-950/30'
            }`}
            onClick={() => handleSelectMail(mail)}
            data-testid={`mail-item-${mail.id}`}
          >
            <div className="flex items-start justify-between mb-1">
              <div className="flex items-center gap-2">
                {!mail.is_read && activeTab === 'inbox' && (
                  <div className="h-2 w-2 rounded-full bg-blue-500"></div>
                )}
                <span className="font-medium">
                  {showFrom ? mail.from_name : mail.to_name}
                </span>
                {mail.priority === 'high' && (
                  <Star className="h-4 w-4 text-amber-500 fill-amber-500" />
                )}
              </div>
              <span className="text-xs text-muted-foreground">
                {formatDateTime(mail.created_at)}
              </span>
            </div>
            <p className="font-medium text-sm mb-1">{mail.subject}</p>
            <p className="text-sm text-muted-foreground line-clamp-1">{mail.body}</p>
            {showFrom && (
              <Badge variant="outline" className="mt-2 text-xs capitalize">
                {mail.from_role}
              </Badge>
            )}
          </div>
        ))
      )}
    </div>
  );

  const MailDetail = () => {
    if (!selectedMail) {
      return (
        <div className="flex items-center justify-center h-full text-muted-foreground">
          <div className="text-center">
            <MailIcon className="h-16 w-16 mx-auto mb-4 opacity-30" />
            <p>Select a message to read</p>
          </div>
        </div>
      );
    }

    return (
      <div className="p-6">
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">{selectedMail.subject}</h2>
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <div>
              <span>From: </span>
              <span className="text-foreground font-medium">
                {selectedMail.from_name || selectedMail.to_name}
              </span>
              <span className="ml-2">({selectedMail.from_email || selectedMail.to_email})</span>
            </div>
            <span>{formatDateTime(selectedMail.created_at)}</span>
          </div>
        </div>
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <p className="whitespace-pre-wrap">{selectedMail.body}</p>
        </div>
        {activeTab === 'inbox' && (
          <div className="mt-6 pt-6 border-t">
            <Button 
              variant="outline"
              onClick={() => {
                setComposeData({
                  to_user_id: selectedMail.from_user_id,
                  subject: `Re: ${selectedMail.subject}`,
                  body: '',
                  priority: 'normal'
                });
                setComposeOpen(true);
              }}
              data-testid="reply-btn"
            >
              Reply
            </Button>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <header className="glass-header sticky top-0 z-40">
        <div className="flex h-16 items-center gap-4 px-4 sm:px-6">
          <Button variant="ghost" size="icon" onClick={() => navigate(-1)} data-testid="back-btn">
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="text-lg font-semibold">Mailbox</h1>
          <div className="ml-auto flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={loadMailData} data-testid="refresh-btn">
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
            <Dialog open={composeOpen} onOpenChange={setComposeOpen}>
              <DialogTrigger asChild>
                <Button data-testid="compose-btn">
                  <Plus className="h-4 w-4 mr-2" />
                  Compose
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-lg" aria-describedby={undefined}>
                <DialogHeader>
                  <DialogTitle>New Message</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>To</Label>
                    <Select 
                      value={composeData.to_user_id}
                      onValueChange={(value) => setComposeData({...composeData, to_user_id: value})}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select recipient" />
                      </SelectTrigger>
                      <SelectContent>
                        {recipients.map((r) => (
                          <SelectItem key={r.id} value={r.id}>
                            {r.name} ({r.role})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Subject</Label>
                    <Input 
                      value={composeData.subject}
                      onChange={(e) => setComposeData({...composeData, subject: e.target.value})}
                      placeholder="Message subject"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Priority</Label>
                    <Select 
                      value={composeData.priority}
                      onValueChange={(value) => setComposeData({...composeData, priority: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="normal">Normal</SelectItem>
                        <SelectItem value="high">High Priority</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Message</Label>
                    <Textarea 
                      value={composeData.body}
                      onChange={(e) => setComposeData({...composeData, body: e.target.value})}
                      placeholder="Type your message..."
                      rows={6}
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button className="flex-1" onClick={handleSend} data-testid="send-mail-btn">
                      Send
                    </Button>
                    <Button variant="outline" onClick={handleSaveDraft} data-testid="save-draft-btn">
                      Save Draft
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto p-4 sm:p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sidebar - Mail List */}
          <div className="lg:col-span-1">
            <Card>
              <CardContent className="p-0">
                <Tabs value={activeTab} onValueChange={setActiveTab}>
                  <TabsList className="w-full grid grid-cols-3 rounded-none border-b">
                    <TabsTrigger value="inbox" className="gap-2" data-testid="inbox-tab">
                      <Inbox className="h-4 w-4" />
                      Inbox
                      {inbox.filter(m => !m.is_read).length > 0 && (
                        <Badge variant="destructive" className="h-5 w-5 p-0 text-xs">
                          {inbox.filter(m => !m.is_read).length}
                        </Badge>
                      )}
                    </TabsTrigger>
                    <TabsTrigger value="sent" className="gap-2" data-testid="sent-tab">
                      <Send className="h-4 w-4" />
                      Sent
                    </TabsTrigger>
                    <TabsTrigger value="drafts" className="gap-2" data-testid="drafts-tab">
                      <FileEdit className="h-4 w-4" />
                      Drafts
                    </TabsTrigger>
                  </TabsList>
                  <div className="p-4 max-h-[600px] overflow-y-auto">
                    <TabsContent value="inbox" className="mt-0">
                      <MailList mails={inbox} showFrom={true} />
                    </TabsContent>
                    <TabsContent value="sent" className="mt-0">
                      <MailList mails={sent} showFrom={false} />
                    </TabsContent>
                    <TabsContent value="drafts" className="mt-0">
                      <MailList mails={drafts} showFrom={false} />
                    </TabsContent>
                  </div>
                </Tabs>
              </CardContent>
            </Card>
          </div>

          {/* Main - Mail Detail */}
          <div className="lg:col-span-2">
            <Card className="min-h-[500px]">
              <MailDetail />
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
