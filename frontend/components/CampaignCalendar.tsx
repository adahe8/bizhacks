import { useState, useEffect } from 'react';
import { scheduleApi } from '@/lib/api';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay, isToday } from 'date-fns';

interface CalendarSchedule {
  date: string;
  time: string;
  campaign_id: string;
  campaign_name: string;
  channel: string;
  frequency: string;
  status: string;
}

interface Props {
  currentMonth?: Date;
}

export default function CampaignCalendar({ currentMonth = new Date() }: Props) {
  const [schedules, setSchedules] = useState<CalendarSchedule[]>([]);
  const [loading, setLoading] = useState(true);
  
  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);
  const days = eachDayOfInterval({ start: monthStart, end: monthEnd });

  useEffect(() => {
    loadSchedules();
  }, [currentMonth]);

  const loadSchedules = async () => {
    try {
      setLoading(true);
      const year = currentMonth.getFullYear();
      const month = currentMonth.getMonth() + 1; // JavaScript months are 0-indexed
      const data = await scheduleApi.getCalendar(year, month);
      setSchedules(data);
    } catch (error) {
      console.error('Error loading calendar schedules:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSchedulesForDay = (date: Date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    return schedules.filter(schedule => schedule.date === dateStr);
  };

  const getDayClass = (date: Date) => {
    const daySchedules = getSchedulesForDay(date);
    let classes = 'p-2 text-center cursor-pointer transition-colors relative ';
    
    if (isToday(date)) {
      classes += 'bg-primary-100 font-bold ';
    }
    
    if (daySchedules.length > 0) {
      classes += 'bg-green-50 hover:bg-green-100 ';
    } else {
      classes += 'hover:bg-gray-50 ';
    }
    
    return classes;
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'facebook': return '📱';
      case 'email': return '✉️';
      case 'google_seo': return '🔍';
      default: return '📢';
    }
  };

  const getChannelColor = (channel: string) => {
    switch (channel) {
      case 'facebook': return 'bg-blue-500';
      case 'email': return 'bg-purple-500';
      case 'google_seo': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-7 gap-1">
            {[...Array(35)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-100 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {format(currentMonth, 'MMMM yyyy')}
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          {schedules.length} campaign{schedules.length !== 1 ? 's' : ''} scheduled this month
        </p>
      </div>

      <div className="grid grid-cols-7 gap-1 mb-2">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
          <div key={day} className="text-center text-xs font-medium text-gray-500 py-2">
            {day}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1">
        {days.map(day => {
          const daySchedules = getSchedulesForDay(day);
          return (
            <div
              key={day.toISOString()}
              className={getDayClass(day)}
              title={daySchedules.length > 0 ? 
                `${daySchedules.length} campaign(s): ${daySchedules.map(s => s.campaign_name).join(', ')}` : 
                'No campaigns scheduled'
              }
            >
              <div className="text-sm">{format(day, 'd')}</div>
              {daySchedules.length > 0 && (
                <div className="mt-1 flex justify-center gap-1">
                  {daySchedules.slice(0, 3).map((schedule, idx) => (
                    <div
                      key={idx}
                      className={`w-2 h-2 rounded-full ${getChannelColor(schedule.channel)}`}
                      title={`${getChannelIcon(schedule.channel)} ${schedule.campaign_name} at ${schedule.time}`}
                    ></div>
                  ))}
                  {daySchedules.length > 3 && (
                    <span className="text-xs text-gray-500">+{daySchedules.length - 3}</span>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-6 space-y-2">
        <h4 className="text-sm font-medium text-gray-700">Today's Campaigns</h4>
        {(() => {
          const todaySchedules = getSchedulesForDay(new Date());
          if (todaySchedules.length === 0) {
            return <p className="text-sm text-gray-500">No campaigns scheduled for today</p>;
          }
          
          return todaySchedules.map((schedule, idx) => (
            <div key={idx} className="flex items-center justify-between text-sm p-2 bg-gray-50 rounded">
              <div className="flex items-center gap-2">
                <span>{getChannelIcon(schedule.channel)}</span>
                <span className="font-medium">{schedule.campaign_name}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-gray-500">{schedule.time}</span>
                <span className={`
                  px-2 py-1 text-xs rounded-full capitalize
                  ${schedule.frequency === 'daily' ? 'bg-blue-100 text-blue-800' : ''}
                  ${schedule.frequency === 'weekly' ? 'bg-green-100 text-green-800' : ''}
                  ${schedule.frequency === 'monthly' ? 'bg-purple-100 text-purple-800' : ''}
                `}>
                  {schedule.frequency}
                </span>
              </div>
            </div>
          ));
        })()}
      </div>

      <div className="mt-4 pt-4 border-t">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span>Facebook</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
              <span>Email</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span>Google</span>
            </div>
          </div>
          <button
            onClick={loadSchedules}
            className="text-primary-600 hover:text-primary-700"
          >
            Refresh
          </button>
        </div>
      </div>
    </div>
  );
}