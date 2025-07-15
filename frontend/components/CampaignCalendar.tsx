import { Schedule } from '@/lib/types';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay, isToday } from 'date-fns';

interface Props {
  schedules: Schedule[];
}

export default function CampaignCalendar({ schedules }: Props) {
  const now = new Date();
  const monthStart = startOfMonth(now);
  const monthEnd = endOfMonth(now);
  const days = eachDayOfInterval({ start: monthStart, end: monthEnd });

  const getSchedulesForDay = (date: Date) => {
    return schedules.filter(schedule => 
      isSameDay(new Date(schedule.scheduled_time), date)
    );
  };

  const getDayClass = (date: Date) => {
    const daySchedules = getSchedulesForDay(date);
    let classes = 'p-2 text-center cursor-pointer transition-colors ';
    
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

  return (
    <div className="card">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {format(now, 'MMMM yyyy')}
        </h3>
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
              title={daySchedules.length > 0 ? `${daySchedules.length} campaign(s) scheduled` : ''}
            >
              <div className="text-sm">{format(day, 'd')}</div>
              {daySchedules.length > 0 && (
                <div className="mt-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full mx-auto"></div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-6 space-y-2">
        <h4 className="text-sm font-medium text-gray-700">Upcoming Campaigns</h4>
        {schedules.slice(0, 5).map(schedule => (
          <div key={schedule.id} className="flex items-center justify-between text-sm">
            <span className="text-gray-600">
              {format(new Date(schedule.scheduled_time), 'MMM d, h:mm a')}
            </span>
            <span className={`
              px-2 py-1 text-xs rounded-full
              ${schedule.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : ''}
              ${schedule.status === 'completed' ? 'bg-green-100 text-green-800' : ''}
            `}>
              {schedule.status}
            </span>
          </div>
        ))}
        {schedules.length === 0 && (
          <p className="text-sm text-gray-500">No campaigns scheduled</p>
        )}
      </div>
    </div>
  );
}