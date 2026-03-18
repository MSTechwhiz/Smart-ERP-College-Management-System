import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Minimize2, Trash2 } from 'lucide-react';
import { Button } from './button';
import { chatbotAPI } from '../../services/api';
import { toast } from 'sonner';
import { useAuth } from '../../context/AuthContext';

export function AIChatbot() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I\'m AcademiaOS Assistant. How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await chatbotAPI.sendMessage(userMessage, sessionId);
      setSessionId(response.data.session_id);
      setMessages(prev => [...prev, { role: 'assistant', content: response.data.response }]);
    } catch (error) {
      toast.error('Failed to get response');
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearChat = () => {
    setMessages([{ role: 'assistant', content: 'Hello! I\'m AcademiaOS Assistant. How can I help you today?' }]);
    setSessionId(null);
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-primary text-primary-foreground rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center z-50"
        data-testid="chatbot-trigger"
      >
        <MessageCircle className="h-6 w-6" />
      </button>
    );
  }

  if (isMinimized) {
    return (
      <div
        className="fixed bottom-6 right-6 bg-primary text-primary-foreground rounded-lg shadow-lg p-3 cursor-pointer z-50 flex items-center gap-2"
        onClick={() => setIsMinimized(false)}
      >
        <MessageCircle className="h-5 w-5" />
        <span className="text-sm font-medium">AcademiaOS Assistant</span>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 h-[500px] bg-background border rounded-lg shadow-xl flex flex-col z-50" data-testid="chatbot-panel">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-primary text-primary-foreground rounded-t-lg">
        <div className="flex items-center gap-2">
          <MessageCircle className="h-5 w-5" />
          <span className="font-semibold">AcademiaOS Assistant</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={handleClearChat}
            className="p-1.5 hover:bg-white/20 rounded transition-colors"
            title="Clear chat"
          >
            <Trash2 className="h-4 w-4" />
          </button>
          <button
            onClick={() => setIsMinimized(true)}
            className="p-1.5 hover:bg-white/20 rounded transition-colors"
            title="Minimize"
          >
            <Minimize2 className="h-4 w-4" />
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="p-1.5 hover:bg-white/20 rounded transition-colors"
            title="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-lg text-sm ${msg.role === 'user'
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted'
                }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-muted p-3 rounded-lg">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                <span className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                <span className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={loading}
            data-testid="chatbot-input"
          />
          <Button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            size="sm"
            data-testid="chatbot-send"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2 text-center">
          Powered by AI - Ask me anything about the ERP
        </p>
      </div>
    </div>
  );
}

export default AIChatbot;
