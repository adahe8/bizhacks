// frontend/components/GameController.tsx
import { useState, useEffect, useRef } from 'react';
import { format } from 'date-fns';
import { gameStateApi, scheduleApi, agentApi } from '@/lib/api';


interface Props {
  onDateChange: (date: Date) => void;
}

export default function GameController({ onDateChange }: Props) {
  const [gameDate, setGameDate] = useState(new Date());
  const [isRunning, setIsRunning] = useState(false);
  const [speed, setSpeed] = useState<'slow' | 'medium' | 'fast'>('medium');
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastCheckedDate = useRef<string>('');

  const speedValues = {
    slow: 30000,    // 30 seconds per day
    medium: 15000,  // 15 seconds per day
    fast: 5000      // 5 seconds per day
  };

  useEffect(() => {
    if (isRunning) {
      intervalRef.current = setInterval(() => {
        setGameDate(prevDate => {
          const newDate = new Date(prevDate);
          newDate.setDate(newDate.getDate() + 1);
          return newDate;
        });
      }, speedValues[speed]);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isRunning, speed]);

  useEffect(() => {
    onDateChange(gameDate);
    
    // Check for scheduled campaigns to execute
    const currentDateStr = format(gameDate, 'yyyy-MM-dd');
    if (currentDateStr !== lastCheckedDate.current && isRunning) {
      lastCheckedDate.current = currentDateStr;
      checkAndExecuteScheduledCampaigns(gameDate);
    }
  }, [gameDate, onDateChange, isRunning]);

  const checkAndExecuteScheduledCampaigns = async (date: Date) => {
    try {
      // Get schedules for the current game date
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      const schedules = await scheduleApi.getCalendar(year, month);
      
      const todayStr = format(date, 'yyyy-MM-dd');
      const todaySchedules = schedules.filter((s: any) => 
        s.date === todayStr && s.status === 'pending'
      );
      
      // Execute each scheduled campaign
      for (const schedule of todaySchedules) {
        console.log(`Executing scheduled campaign: ${schedule.campaign_name}`);
        try {
          await agentApi.executeCampaign(schedule.campaign_id);
        } catch (error) {
          console.error(`Failed to execute campaign ${schedule.campaign_id}:`, error);
        }
      }
    } catch (error) {
      console.error('Error checking scheduled campaigns:', error);
    }
  };

  // In handlePlayPause function:
  const handlePlayPause = async () => {
    const newIsRunning = !isRunning;
    setIsRunning(newIsRunning);
    
    // Persist to backend
    await gameStateApi.update({
      current_date: gameDate.toISOString(),
      is_running: newIsRunning,
      game_speed: speed
    });
  };

  // In handleSpeedChange function:
  const handleSpeedChange = async (newSpeed: 'slow' | 'medium' | 'fast') => {
    setSpeed(newSpeed);
    
    // Persist to backend
    await gameStateApi.update({
      game_speed: newSpeed
    });
  };

  // Add useEffect to load initial state
  useEffect(() => {
    const loadGameState = async () => {
      const state = await gameStateApi.getCurrent();
      if (state) {
        setGameDate(new Date(state.current_date));
        setIsRunning(state.is_running);
        setSpeed(state.game_speed);
      }
    };
    loadGameState();
  }, []);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div>
            <p className="text-sm text-gray-500">Game Date</p>
            <p className="text-lg font-semibold text-gray-900">
              {format(gameDate, 'MMMM d, yyyy')}
            </p>
          </div>
          
          <button
            onClick={handlePlayPause}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              isRunning 
                ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                : 'bg-green-100 text-green-700 hover:bg-green-200'
            }`}
          >
            {isRunning ? '⏸ Pause' : '▶ Play'}
          </button>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">Speed:</span>
          <div className="flex space-x-1">
            {(['slow', 'medium', 'fast'] as const).map((s) => (
              <button
                key={s}
                onClick={() => handleSpeedChange(s)}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  speed === s
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {s === 'slow' ? '30s' : s === 'medium' ? '15s' : '5s'}
              </button>
            ))}
          </div>
        </div>
      </div>
      
      {isRunning && (
        <div className="mt-2 text-xs text-gray-500">
          Game is running - campaigns will execute automatically on their scheduled dates
        </div>
      )}
    </div>
  );
}