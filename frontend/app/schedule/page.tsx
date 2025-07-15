'use client';

import { useEffect, useState } from 'react';
import { scheduleApi, campaignApi } from '@/lib/api';
import ScheduleTimeline from '@/components/ScheduleTimeline';
import { Schedule, Campaign } from '@/lib/types';
import { format } from 'date-fns';

export default function SchedulePage() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [schedulesData, campaignsData] = await Promise.all([
        scheduleApi.list(),
        campaignApi.list(),
      ]);
      setSchedules(schedulesData);
      setCampaigns(campaignsData);
    } catch (error) {
      console.error('Error loading schedule data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSchedule = async (campaignId: string, scheduledTime: Date) => {
    try {
      await scheduleApi.create({
        campaign_id: campaignId,
        scheduled_time: scheduledTime.toISOString(),
        recurring: false,
      });
      await loadData();
    } catch (error) {
      console.error('Error creating schedule:', error);
    }
  };

  const handleDeleteSchedule = async (scheduleId: string) => {
    if (confirm('Are you sure you want to delete this schedule?')) {
      try {
        await scheduleApi.delete(scheduleId);
        await loadData();
      } catch (error) {
        console.error('Error deleting schedule:', error);
      }
    }
  };

  const filteredSchedules = schedules.filter(schedule => {
    if (filter === 'all') return true;
    if (filter === 'pending') return schedule.status === 'pending';
    if (filter === 'completed') return schedule.status === 'completed' || schedule.status === 'failed';
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Campaign Schedule</h1>
        <p className="text-gray-600 mt-2">Manage and monitor your campaign execution timeline</p>
      </div>

      {/* Filter Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {(['all', 'pending', 'completed'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={`
                py-2 px-1 border-b-2 font-medium text-sm capitalize
                ${filter === tab
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Timeline View */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Schedule Timeline</h2>
        <ScheduleTimeline schedules={filteredSchedules.filter(s => s.status === 'pending')} />
      </div>

      {/* Schedule List */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">All Schedules</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Campaign
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Scheduled Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredSchedules.map((schedule) => {
                const campaign = campaigns.find(c => c.id === schedule.campaign_id);
                return (
                  <tr key={schedule.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {campaign?.name || 'Unknown Campaign'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {campaign?.channel}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {format(new Date(schedule.scheduled_time), 'PPpp')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`
                        px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                        ${schedule.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : ''}
                        ${schedule.status === 'executing' ? 'bg-blue-100 text-blue-800' : ''}
                        ${schedule.status === 'completed' ? 'bg-green-100 text-green-800' : ''}
                        ${schedule.status === 'failed' ? 'bg-red-100 text-red-800' : ''}
                      `}>
                        {schedule.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {schedule.status === 'pending' && (
                        <button
                          onClick={() => handleDeleteSchedule(schedule.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Cancel
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Schedule */}
      <div className="mt-8 card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Schedule</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <select className="input-field">
            <option value="">Select a campaign</option>
            {campaigns.filter(c => c.status === 'active').map(campaign => (
              <option key={campaign.id} value={campaign.id}>
                {campaign.name}
              </option>
            ))}
          </select>
          <input
            type="datetime-local"
            className="input-field"
            min={new Date().toISOString().slice(0, 16)}
          />
        </div>
        <button className="btn-primary mt-4">
          Schedule Campaign
        </button>
      </div>
    </div>
  );
}