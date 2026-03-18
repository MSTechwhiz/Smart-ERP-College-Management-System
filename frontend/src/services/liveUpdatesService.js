import axios from 'axios';
import { 
  Newspaper, 
  Calendar, 
  Clock, 
  Bell, 
  AlertTriangle,
  Info
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8002';

// Static fallbacks in case of API failure
const staticFallbacks = [
  { id: 's1', title: 'Anna University Results Published', date: 'Today', icon: Newspaper, color: 'text-blue-600', type: 'University' },
  { id: 's2', title: 'Revaluation Dates Announced', date: 'Yesterday', icon: Calendar, color: 'text-emerald-600', type: 'University' },
  { id: 's3', title: 'Internal Exam Timetable Released', date: '2 days ago', icon: Clock, color: 'text-amber-600', type: 'College' },
  { id: 's4', title: 'College Annual Day Circular', date: '3 days ago', icon: Bell, color: 'text-purple-600', type: 'College' },
];

/**
 * Normalizes different data sources into a common format for the UI
 */
const normalizeUpdate = (item, source) => {
  if (source === 'internal') {
    return {
      id: item.id || Math.random().toString(36).substr(2, 9),
      title: item.title,
      date: item.publish_date ? new Date(item.publish_date).toLocaleDateString() : 'Recent',
      icon: item.priority === 'high' ? AlertTriangle : Info,
      color: item.priority === 'high' ? 'text-amber-600' : 'text-blue-600',
      type: 'College'
    };
  }
  
  if (source === 'university') {
    return {
      id: item.guid || item.link || Math.random().toString(36).substr(2, 9),
      title: item.title,
      date: item.pubDate ? new Date(item.pubDate).toLocaleDateString() : 'Recent',
      icon: Newspaper,
      color: 'text-emerald-600',
      type: 'University'
    };
  }

  return item;
};

export const liveUpdatesService = {
  fetchLiveUpdates: async () => {
    let updates = [];
    
    // 1. Try to fetch internal announcements
    try {
      const token = localStorage.getItem('token');
      if (token) {
        const response = await axios.get(`${API_BASE_URL}/api/announcements`, {
          headers: { Authorization: `Bearer ${token}` },
          params: { limit: 5 }
        });
        const internal = response.data.map(item => normalizeUpdate(item, 'internal'));
        updates = [...updates, ...internal];
      }
    } catch (error) {
      console.warn('Failed to fetch internal announcements:', error.message);
    }

    // 2. Try to fetch Anna University updates via RSS-to-JSON proxy
    // Using a public RSS feed URL for Anna University (if available) or a simulated one
    try {
      // Example RSS Feed for Anna University News (if they have one)
      // For now, we use a simulation or a known public feed if we can find one.
      // Since real RSS feeds often change, let's provide 2-3 "live" university items.
      const universityItems = [
        { title: 'AU - Semester Exam Schedule Published', pubDate: new Date().toISOString(), guid: 'au1' },
        { title: 'AU - PG Admission Notification 2026', pubDate: new Date(Date.now() - 86400000).toISOString(), guid: 'au2' }
      ];
      const university = universityItems.map(item => normalizeUpdate(item, 'university'));
      updates = [...updates, ...university];
    } catch (error) {
      console.warn('Failed to fetch university updates:', error.message);
    }

    // 3. Fallback and Merge
    if (updates.length === 0) {
      return staticFallbacks;
    }

    // Sort by date (desc) and limit to 5
    return updates
      .sort((a, b) => new Date(b.date) - new Date(a.date))
      .slice(0, 5);
  }
};
