import { Schedule } from '@/lib/types';
import { format, differenceInHours, differenceInDays } from 'date-fns';

interface Props {
  schedules: Schedule[];
}

export default function ScheduleTimeline({ schedules }: Props) {
  const now = new Date();
  
  // Sort schedules by time
  const sortedSchedules = [...schedules].sort((a, b) => 
    new Date(a.scheduled_time).getTime() - new Date(b.scheduled_time).getTime()
  );

  const getTimeUntil = (scheduledTime: string) => {
    const scheduled = new Date(scheduledTime);
    const hoursUntil = differenceInHours(scheduled, now);
    const daysUntil = differenceInDays(scheduled, now);

    if (hoursUntil < 0) return 'Overdue';
    if (hoursUntil < 1) return 'Soon';
    if (hoursUntil < 24) return `${hoursUntil}h`;
    return `${daysUntil}d`;
  };

  const getPositionPercentage = (scheduledTime: string) => {
    const scheduled = new Date(scheduledTime);
    const totalHours = 7 * 24; // 7 days in hours
    const hoursFromNow = differenceInHours(scheduled, now);
    
    if (hoursFromNow < 0) return 0;
    if (hoursFromNow > totalHours) return 100;
    
    return (hoursFromNow / totalHours) * 100;
  };

  if (schedules.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-8 text-center">
        <p className="text-gray-500">No upcoming campaigns scheduled</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      {/* Timeline header */}
      <div className="flex justify-between text-sm text-gray-500 mb-4">
        <span>Now</span>
        <span>Next 7 days</span>
      </div>

      {/* Timeline track */}
      <div className="relative h-2 bg-gray-200 rounded-full mb-8">
        <div className="absolute left-0 top-0 h-full w-1 bg-primary-600 rounded-full"></div>
        
        {/* Schedule markers */}
        {sortedSchedules.map((schedule, index) => {
          const position = getPositionPercentage(schedule.scheduled_time);
          if (position > 100) return null;
          
          return (
            <div
              key={schedule.id}
              className="absolute top-1/2 transform -translate-y-1/2"
              style={{ left: `${position}%` }}
            >
              <div className="relative group">
                <div className="w-4 h-4 bg-primary-500 rounded-full cursor-pointer hover:scale-125 transition-transform"></div>
                
                {/* Tooltip */}
                <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 invisible group-hover:visible bg-gray-900 text-white text-xs rounded px-2 py-1 whitespace-nowrap">
                  {format(new Date(schedule.scheduled_time), 'MMM d, h:mm a')}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Schedule list */}
      <div className="space-y-3">
        {sortedSchedules.slice(0, 5).map((schedule) => (
          <div
            key={schedule.id}
            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                <span className="text-xs font-medium text-primary-700">
                  {getTimeUntil(schedule.scheduled_time)}
                </span>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">
                  Campaign #{schedule.campaign_id.slice(0, 8)}
                </p>
                <p className="text-xs text-gray-500">
                  {format(new Date(schedule.scheduled_time), 'PPp')}
                </p>
              </div>
            </div>
            <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full">
              Pending
            </span>
          </div>
        ))}
      </div>

      {sortedSchedules.length > 5 && (
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-500">
            And {sortedSchedules.length - 5} more scheduled campaigns
          </p>
        </div>
      )}
    </div>
  );
}