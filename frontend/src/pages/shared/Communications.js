import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Badge } from "../../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../../components/ui/dialog";
import { Label } from "../../components/ui/label";
import { FileText, Send, Eye, MessageSquare, AlertCircle, CheckCircle, Trash2, User } from 'lucide-react';
import { communicationAPI } from "../../services/api";
import { toast } from "sonner";
import { format } from "date-fns";

export function Communications({ userRole, userId }) {
    const [activeTab, setActiveTab] = useState('inbox');
    const [inbox, setInbox] = useState([]);
    const [sent, setSent] = useState([]);
    const [loading, setLoading] = useState(true);

    // View/Compose state
    const [viewingComm, setViewingComm] = useState(null);
    // Compose state
    const [isComposeOpen, setIsComposeOpen] = useState(false);
    const [composeData, setComposeData] = useState({ title: '', message: '', target_role: '', priority: 'normal', attachment_url: '' });
    const [sendMethod, setSendMethod] = useState('internal');

    useEffect(() => {
        fetchCommunications();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [activeTab]);

    const fetchCommunications = async () => {
        setLoading(true);
        try {
            if (activeTab === 'inbox') {
                const response = await communicationAPI.getInbox({ skip: 0, limit: 100 });
                setInbox(response.data);
            } else if (activeTab === 'sent' && userRole !== 'student') {
                const response = await communicationAPI.getSent({ skip: 0, limit: 100 });
                setSent(response.data);
            }
        } catch (error) {
            console.error("Failed to fetch communications:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSend = async () => {
        if (!composeData.title || !composeData.message || !composeData.target_role) {
            toast.error("Please fill all required fields");
            return;
        }

        if (sendMethod === 'whatsapp') {
            const formattedMessage = `College Communication\n\nTitle: ${composeData.title}\n\nMessage:\n${composeData.message}\n\nSent from AcademiaOS ERP`;
            const encodedMessage = encodeURIComponent(formattedMessage);
            window.open(`https://web.whatsapp.com/send?text=${encodedMessage}`, '_blank');

            toast.success("Opening WhatsApp Web...");
            setIsComposeOpen(false);
            setComposeData({ title: '', message: '', target_role: '', priority: 'normal', attachment_url: '' });
            setSendMethod('internal');
            return;
        }
        try {
            await communicationAPI.send(composeData);
            toast.success("Communication sent successfully!");
            setIsComposeOpen(false);
            setComposeData({ title: '', message: '', target_role: '', priority: 'normal', attachment_url: '' });
            if (activeTab === 'sent') fetchCommunications();
        } catch (error) {
            toast.error(error.response?.data?.detail || "Failed to send communication");
        }
    };

    const getRoleOptions = () => {
        switch (userRole) {
            case 'admin': return [{ label: 'Principals', value: 'principal' }, { label: 'HODs', value: 'hod' }, { label: 'Faculty', value: 'faculty' }, { label: 'Students', value: 'student' }];
            case 'principal': return [{ label: 'HODs', value: 'hod' }, { label: 'Faculty', value: 'faculty' }, { label: 'Students', value: 'student' }];
            case 'hod': return [{ label: 'Faculty', value: 'faculty' }, { label: 'Students', value: 'student' }];
            case 'faculty': return [{ label: 'Students', value: 'student' }];
            default: return [];
        }
    };

    const handleView = async (comm) => {
        setViewingComm(comm);
        try {
            // Fetch details which marks as read
            const response = await communicationAPI.getOne(comm.id);
            setViewingComm(response.data);

            // Update local state if it was unread
            if (activeTab === 'inbox' && !comm.read_status?.includes(userId)) {
                setInbox(prev => prev.map(c =>
                    c.id === comm.id
                        ? { ...c, read_status: [...(c.read_status || []), userId] }
                        : c
                ));
            }
        } catch (error) {
            console.error("Failed to fetch communication details:", error);
        }
    };

    const handleDelete = async (e, id) => {
        e.stopPropagation();
        if (!window.confirm("Are you sure you want to delete this communication?")) return;

        try {
            await communicationAPI.delete(id);
            toast.success("Communication deleted");
            if (activeTab === 'sent') setSent(sent.filter(c => c.id !== id));
            else fetchCommunications();
        } catch (error) {
            toast.error("Failed to delete communication");
        }
    };

    const renderList = (items, isInbox) => {
        if (loading) return <div className="p-8 text-center text-muted-foreground">Loading...</div>;
        if (items.length === 0) return (
            <div className="p-12 text-center text-muted-foreground flex flex-col items-center">
                <MessageSquare className="h-12 w-12 text-muted-foreground/30 mb-4" />
                <p>No communications found in {isInbox ? 'Inbox' : 'Sent items'}</p>
            </div>
        );

        return (
            <div className="space-y-4">
                {items.map((comm) => {
                    const isRead = isInbox ? comm.read_status?.includes(userId) : true;

                    return (
                        <Card
                            key={comm.id}
                            className={`cursor-pointer transition-all hover:bg-muted/50 ${!isRead && isInbox ? 'border-primary/50 shadow-sm' : ''}`}
                            onClick={() => handleView(comm)}
                        >
                            <CardContent className="p-4 flex items-center justify-between">
                                <div className="flex items-start gap-4">
                                    <div className={`mt-1 h-2 w-2 rounded-full ${!isRead && isInbox ? 'bg-primary' : 'bg-transparent'}`} />
                                    <div>
                                        <div className="flex items-center gap-2 mb-1">
                                            <h4 className={`font-medium ${!isRead && isInbox ? 'text-primary' : ''}`}>{comm.title}</h4>
                                            {comm.priority === 'high' && <Badge variant="destructive" className="h-5 px-1.5 text-[10px]">High Priority</Badge>}
                                        </div>
                                        <p className="text-sm text-muted-foreground line-clamp-1 mb-2">
                                            {comm.message}
                                        </p>
                                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                            <span className="flex items-center gap-1">
                                                <User className="h-3 w-3" />
                                                {isInbox ? `From: ${comm.sender_name} (${comm.sender_role})` : `To: ${comm.target_role}`}
                                            </span>
                                            <span>{format(new Date(comm.created_at), 'MMM dd, yyyy HH:mm')}</span>
                                        </div>
                                    </div>
                                </div>
                                {(!isInbox || userRole === 'admin') && (
                                    <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-destructive shrink-0" onClick={(e) => handleDelete(e, comm.id)}>
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                )}
                            </CardContent>
                        </Card>
                    );
                })}
            </div>
        );
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight">Communications</h2>
                    <p className="text-muted-foreground">Manage internal direct messaging</p>
                </div>
                {userRole !== 'student' && (
                    <Button onClick={() => setIsComposeOpen(true)} className="gap-2">
                        <Send className="h-4 w-4" />
                        New Message
                    </Button>
                )}
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="mb-4">
                    <TabsTrigger value="inbox" className="px-6">Inbox</TabsTrigger>
                    {userRole !== 'student' && <TabsTrigger value="sent" className="px-6">Sent</TabsTrigger>}
                </TabsList>

                <TabsContent value="inbox" className="mt-0">
                    <Card>
                        <CardHeader className="pb-3 border-b">
                            <CardTitle className="text-lg">Received Communications</CardTitle>
                        </CardHeader>
                        <CardContent className="pt-4">
                            {renderList(inbox, true)}
                        </CardContent>
                    </Card>
                </TabsContent>

                {userRole !== 'student' && (
                    <TabsContent value="sent" className="mt-0">
                        <Card>
                            <CardHeader className="pb-3 border-b flex flex-row items-center justify-between">
                                <CardTitle className="text-lg">Sent Communications</CardTitle>
                            </CardHeader>
                            <CardContent className="pt-4">
                                {renderList(sent, false)}
                            </CardContent>
                        </Card>
                    </TabsContent>
                )}
            </Tabs>

            {/* View Modal */}
            <Dialog open={!!viewingComm} onOpenChange={(open) => !open && setViewingComm(null)}>
                <DialogContent className="max-w-2xl">
                    <DialogHeader>
                        <div className="flex items-center gap-2 mb-2">
                            <Badge variant="outline" className="uppercase">{viewingComm?.priority || 'normal'}</Badge>
                            <span className="text-sm text-muted-foreground ml-auto">
                                {viewingComm?.created_at && format(new Date(viewingComm.created_at), 'MMM dd, yyyy hh:mm a')}
                            </span>
                        </div>
                        <DialogTitle className="text-xl mb-4">{viewingComm?.title}</DialogTitle>
                    </DialogHeader>

                    <div className="p-4 bg-muted/30 rounded-lg border mt-2">
                        <div className="flex flex-col gap-2 text-sm text-muted-foreground mb-4 pb-4 border-b">
                            <div className="flex items-center gap-2"><User className="h-4 w-4" /> <strong>From:</strong> {viewingComm?.sender_name} ({viewingComm?.sender_role})</div>
                            <div className="flex items-center gap-2"><Users className="h-4 w-4" /> <strong>To:</strong> {viewingComm?.target_role}</div>
                        </div>

                        <div className="whitespace-pre-wrap text-sm leading-relaxed mb-6">
                            {viewingComm?.message}
                        </div>

                        {viewingComm?.attachment_url && (
                            <div className="mt-4 pt-4 border-t">
                                <h5 className="font-medium text-sm mb-2">Attachments</h5>
                                <a href={viewingComm.attachment_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 text-sm text-primary hover:underline bg-primary/5 px-3 py-1.5 rounded-md border border-primary/20">
                                    <FileText className="h-4 w-4" />
                                    View Attachment
                                </a>
                            </div>
                        )}

                        {/* Show Read Status internally for sender */}
                        {userRole !== 'student' && viewingComm?.sender_id === userId && (
                            <div className="mt-6 pt-4 border-t text-xs text-muted-foreground">
                                Read by {viewingComm?.read_status?.length || 0} user(s)
                            </div>
                        )}
                    </div>
                </DialogContent>
            </Dialog>

            {/* Compose Modal */}
            <Dialog open={isComposeOpen} onOpenChange={setIsComposeOpen}>
                <DialogContent className="max-w-xl">
                    <DialogHeader>
                        <DialogTitle>New Communication</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label>Send Method</Label>
                            <div className="flex gap-4 items-center">
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input
                                        type="radio"
                                        name="sendMethod"
                                        value="internal"
                                        checked={sendMethod === 'internal'}
                                        onChange={() => setSendMethod('internal')}
                                    />
                                    Internal Communication
                                </label>
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input
                                        type="radio"
                                        name="sendMethod"
                                        value="whatsapp"
                                        checked={sendMethod === 'whatsapp'}
                                        onChange={() => setSendMethod('whatsapp')}
                                    />
                                    WhatsApp Message
                                </label>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label>Target Role</Label>
                            <select
                                className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                value={composeData.target_role}
                                onChange={e => setComposeData({ ...composeData, target_role: e.target.value })}
                            >
                                <option value="" disabled>Select Target</option>
                                {getRoleOptions().map(opt => (
                                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                                ))}
                            </select>
                        </div>
                        <div className="space-y-2">
                            <Label>Title</Label>
                            <Input
                                placeholder="Enter message title"
                                value={composeData.title}
                                onChange={e => setComposeData({ ...composeData, title: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Message</Label>
                            <textarea
                                className="flex min-h-[150px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                placeholder="Type your message here..."
                                value={composeData.message}
                                onChange={e => setComposeData({ ...composeData, message: e.target.value })}
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Priority</Label>
                                <select
                                    className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    value={composeData.priority}
                                    onChange={e => setComposeData({ ...composeData, priority: e.target.value })}
                                >
                                    <option value="normal">Normal</option>
                                    <option value="high">High</option>
                                </select>
                            </div>
                            <div className="space-y-2">
                                <Label>Attachment URL (Optional)</Label>
                                <Input
                                    placeholder="https://..."
                                    value={composeData.attachment_url}
                                    onChange={e => setComposeData({ ...composeData, attachment_url: e.target.value })}
                                />
                            </div>
                        </div>
                        <div className="flex justify-end pt-4 gap-2">
                            <Button variant="outline" onClick={() => setIsComposeOpen(false)}>Cancel</Button>
                            <Button onClick={handleSend} className="gap-2">
                                <Send className="h-4 w-4" /> Send Message
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}

// Just defining Users Icon locally to avoid adding more imports
function Users(props) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
    )
}
