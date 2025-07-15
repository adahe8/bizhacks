'use client';

import { useEffect, useState } from 'react';
import { campaignApi, metricsApi, agentApi, setupApi } from '@/lib/api';
import MetricsVisualization from '@/components/MetricsVisualization';
import CampaignCard from '@/components/CampaignCard';
import CustomerSegments from '@/components/CustomerSegments';
import CampaignCalendar from '@/components/CampaignCalendar';
import GameController from '../../components/GameController';
import SetupInfoDisplay from '../../components/SetupInfoDisplay';
import SpendOptimizationChart from '../../components/SpendOptimizationChart';
import { Campaign, ChannelMetrics, CustomerSegment, Schedule, Company, Product } from '@/lib/types';

export default function Dashboard() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [channelMetrics, setChannelMetrics] = useState<ChannelMetrics[]>([]);
  const [segments, setSegments] = useState<CustomerSegment[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [company, setCompany] = useState<Company | null>(null);
  const [product, setProduct] = useState<Product | null>(null);
  const [optimizationData, setOptimizationData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [gameDate, setGameDate] = useState(new Date());

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // First get setup configuration
      const setup = await setupApi.getCurrent();
      if (setup && setup.company_id && setup.product_id) {
        // Load company and product info
        const [companies, products] = await Promise.all([
          setupApi.getCompanies(),
          setupApi.getProducts()
        ]);
        
        const currentCompany = companies.find((c: any) => c.id === setup.company_id);
        const currentProduct = products.find((p: any) => p.id === setup.product_id);
        
        setCompany(currentCompany);
        setProduct(currentProduct);
      }

      // Load other dashboard data
      const [campaignsData, metricsData, segmentsData] = await Promise.all([
        campaignApi.list({ status: 'active' }),
        metricsApi.getChannelMetrics(7),
        agentApi.getSegments()
      ]);

      setCampaigns(campaignsData);
      setChannelMetrics(metricsData);
      setSegments(segmentsData);
      
      // Generate mock optimization data
      const mockOptData = generateMockOptimizationData();
      setOptimizationData(mockOptData);
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateMockOptimizationData = () => {
    const data = [];
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30);
    
    for (let i = 0; i <= 30; i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i);
      
      data.push({
        date,
        optimal: 1000 + (i * 150) + Math.random() * 100,
        nonOptimal: 1000 + (i * 100) + Math.random() * 50
      });
    }
    
    return data;
  };

  const handleCampaignUpdate = async () => {
    const updatedCampaigns = await campaignApi.list({ status: 'active' });
    setCampaigns(updatedCampaigns);
  };

  const handleDateChange = (date: Date) => {
    setGameDate(date);
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
      {/* Company and Product Info */}
      <SetupInfoDisplay company={company} product={product} />

      {/* Game Controller */}
      <div className="mb-6">
        <GameController onDateChange={handleDateChange} />
      </div>

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Marketing Dashboard</h1>
        <p className="text-gray-600 mt-2">Monitor and manage your omni-channel campaigns</p>
      </div>

      {/* Optimization Performance Chart */}
      <div className="mb-8">
        <SpendOptimizationChart data={optimizationData} />
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

      {/* Customer Segments and Active Campaigns Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Customer Segments</h2>
          <CustomerSegments segments={segments} />
        </div>

        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Campaign Summary</h2>
          <div className="card">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Active Campaigns</span>
                <span className="text-2xl font-bold text-gray-900">{campaigns.length}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Monthly Budget</span>
                <span className="text-xl font-bold text-gray-900">
                  ${campaigns.reduce((sum, c) => sum + c.budget, 0).toLocaleString()}
                </span>
              </div>
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-500 mb-2">By Channel:</p>
                {['facebook', 'email', 'google_seo'].map(channel => {
                  const channelCampaigns = campaigns.filter(c => c.channel === channel);
                  return (
                    <div key={channel} className="flex justify-between text-sm">
                      <span className="capitalize">{channel.replace('_', ' ')}</span>
                      <span>{channelCampaigns.length} campaigns</span>
                    </div>
                  );
                })}
              </div>
              <div className="pt-3">
                <a href="/campaigns" className="btn-primary w-full text-center">
                  View All Campaigns
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
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