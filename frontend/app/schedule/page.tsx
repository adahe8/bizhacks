// app/schedule/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { format, addDays, startOfWeek, endOfWeek } from 'date-fns';
import { 
  FaArrowLeft, 
  FaCalendarAlt,
  FaFacebook,
  FaEnvelope,
  FaGoogle,
  FaClock
} from 'react-icons/fa';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ScheduledCampaign {
  campaign_id: number;
  campaign_name: string;
  next_run: string;
  frequency_days: number;
  channel: string;
}

interface Campaign {
  id: number;
  name: string;
  channel: string;
  status: string;
  frequency_days: number;
}

export default function SchedulePage() {
  const router = useRouter();
  const [schedules, setSchedules] = useState<ScheduledCampaign[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedWeek, setSelectedWeek] = useState(new Date());

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [schedulesRes, campaignsRes] = await Promise.all([
        axios.get(`${API_BASE}/api/schedules/`),
        axios.get(`${API_BASE}/api/campaigns/`)
      ]);

      setSchedules(schedulesRes.data);
      setCampaigns(campaignsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Failed to load schedules');
    } finally {
      setLoading(false);
    }
  };

  const getChannelIcon = (channel: string) => {
    switch(channel) {
      case 'facebook':
        return <FaFacebook className="text-blue-600" />;
      case 'email':
        return <FaEnvelope className="text-green-600" />;
      case 'google_ads':
        return <FaGoogle className="text-red-600" />;
      default:
        return null;
    }
  };

  const getChannelColor = (channel: string) => {
    switch(channel) {
      case 'facebook':
        return 'bg-blue-100 border-blue-300';
      case 'email':
        return 'bg-green-100 border-green-300';
      case 'google_ads':
        return 'bg-red-100 border-red-300';
      default:
        return 'bg-gray-100 border-gray-300';
    }
  };

  const getWeekDays = () => {
    const start = startOfWeek(selectedWeek);
    const days = [];
    
    for (let i = 0; i < 7; i++) {
      days.push(addDays(start, i));
    }
    
    return days;
  };

  const getCampaignsForDay = (date: Date) => {
    return schedules.filter(schedule => {
      const scheduleDate = new Date(schedule.next_run);
      return format(scheduleDate, 'yyyy-MM-dd') === format(date, 'yyyy-MM-dd');
    });
  };

  const navigateWeek = (direction: 'prev' | 'next') => {
    setSelectedWeek(prev => addDays(prev, direction === 'next' ? 7 : -7));
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button
                onClick={() => router.push('/dashboard')}
                className="mr-4 p-2 text-gray-600 hover:text-gray-900"
              >
                <FaArrowLeft />
              </button>
              <h1 className="text-2xl font-bold text-gray-900">Campaign Schedule</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigateWeek('prev')}
                className="p-2 text-gray-600 hover:text-gray-900"
              >
                ←
              </button>
              <span className="text-lg font-medium">
                {format(startOfWeek(selectedWeek), 'MMM d')} - {format(endOfWeek(selectedWeek), 'MMM d, yyyy')}
              </span>
              <button
                onClick={() => navigateWeek('next')}
                className="p-2 text-gray-600 hover:text-gray-900"
              >
                →
              </button>
              <button
                onClick={() => setSelectedWeek(new Date())}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                Today
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Calendar View */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="grid grid-cols-7 gap-px bg-gray-200">
            {getWeekDays().map((day, index) => {
              const daySchedules = getCampaignsForDay(day);
              const isToday = format(day, 'yyyy-MM-dd') === format(new Date(), 'yyyy-MM-dd');
              
              return (
                <div
                  key={index}
                  className={`bg-white p-4 min-h-[200px] ${
                    isToday ? 'bg-indigo-50' : ''
                  }`}
                >
                  <div className="mb-3">
                    <div className="text-sm font-medium text-gray-900">
                      {format(day, 'EEE')}
                    </div>
                    <div className={`text-2xl font-bold ${
                      isToday ? 'text-indigo-600' : 'text-gray-900'
                    }`}>
                      {format(day, 'd')}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    {daySchedules.map((schedule, idx) => (
                      <div
                        key={idx}
                        className={`p-2 rounded border text-xs ${getChannelColor(schedule.channel)}`}
                      >
                        <div className="flex items-center mb-1">
                          {getChannelIcon(schedule.channel)}
                          <span className="ml-1 font-medium truncate">
                            {schedule.campaign_name}
                          </span>
                        </div>
                        <div className="flex items-center text-gray-600">
                          <FaClock className="mr-1" />
                          {format(new Date(schedule.next_run), 'h:mm a')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Upcoming Campaigns List */}
        <div className="mt-8 bg-white rounded-lg shadow">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Upcoming Campaign Executions
            </h2>
            
            {schedules.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No scheduled campaigns. Start campaigns from the dashboard to see them here.
              </p>
            ) : (
              <div className="space-y-3">
                {schedules
                  .sort((a, b) => new Date(a.next_run).getTime() - new Date(b.next_run).getTime())
                  .slice(0, 10)
                  .map((schedule, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex items-center">
                        {getChannelIcon(schedule.channel)}
                        <div className="ml-3">
                          <h4 className="font-medium text-gray-900">
                            {schedule.campaign_name}
                          </h4>
                          <p className="text-sm text-gray-600">
                            Every {schedule.frequency_days} days
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-gray-900">
                          {format(new Date(schedule.next_run), 'MMM d, yyyy')}
                        </p>
                        <p className="text-sm text-gray-600">
                          {format(new Date(schedule.next_run), 'h:mm a')}
                        </p>
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}