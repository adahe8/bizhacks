'use client';

import { useEffect, useState } from 'react';
import { campaignApi, metricsApi, agentApi, scheduleApi } from '@/lib/api';
import MetricsVisualization from '@/components/MetricsVisualization';
import CampaignCard from '@/components/CampaignCard';
import CustomerSegments from '@/components/CustomerSegments';
import CampaignCalendar from '@/components/CampaignCalendar';
import { Campaign, ChannelMetrics, CustomerSegment, Schedule } from '@/lib/types';

export default function Dashboard() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [channelMetrics, setChannelMetrics] = useState<ChannelMetrics[]>([]);
  const [segments, setSegments] = useState<CustomerSegment[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [campaignsData, metricsData, segmentsData, schedulesData] = await Promise.all([
        campaignApi.list({ status: 'active' }),
        metricsApi.getChannelMetrics(7),
        agentApi.getSegments(),
        scheduleApi.getUpcoming(30),
      ]);

      setCampaigns(campaignsData);
      setChannelMetrics(metricsData);
      setSegments(segmentsData);
      setSchedules(schedulesData);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCampaignUpdate = async () => {
    // Reload campaigns after update
    const updatedCampaigns = await campaignApi.list({ status: 'active' });
    setCampaigns(updatedCampaigns);
  };

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
        <h1 className="text-3xl font-bold text-gray-900">Marketing Dashboard</h1>
        <p className="text-gray-600 mt-2">Monitor and manage your omni-channel campaigns</p>
      </div>

      {/* Channel Metrics */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Channel Performance</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {channelMetrics.map((metric) => (
            <MetricsVisualization key={metric.channel} metrics={metric} />
          ))}
        </div>
      </div>

      {/* Active Campaigns */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Active Campaigns</h2>
          <a href="/create" className="btn-primary">
            Create Campaign
          </a>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {campaigns.length > 0 ? (
            campaigns.map((campaign) => (
              <CampaignCard
                key={campaign.id}
                campaign={campaign}
                onUpdate={handleCampaignUpdate}
              />
            ))
          ) : (
            <div className="col-span-3 text-center py-12 bg-gray-50 rounded-lg">
              <p className="text-gray-500">No active campaigns yet.</p>
              <a href="/create" className="text-primary-600 hover:text-primary-700 mt-2 inline-block">
                Create your first campaign →
              </a>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Customer Segments */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Customer Segments</h2>
          <CustomerSegments segments={segments} />
        </div>

        {/* Campaign Calendar */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Upcoming Campaigns</h2>
          <CampaignCalendar schedules={schedules} />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="flex flex-wrap gap-4">
          <button
            onClick={async () => {
              await metricsApi.collectMetrics();
              alert('Metrics collection triggered');
            }}
            className="btn-outline"
          >
            Refresh Metrics
          </button>
          <button
            onClick={async () => {
              await agentApi.rebalanceBudgets();
              alert('Budget rebalancing triggered');
            }}
            className="btn-outline"
          >
            Rebalance Budgets
          </button>
          <button
            onClick={async () => {
              await agentApi.generateSegments();
              const newSegments = await agentApi.getSegments();
              setSegments(newSegments);
            }}
            className="btn-outline"
          >
            Update Segments
          </button>
        </div>
      </div>
    </div>
  );
}