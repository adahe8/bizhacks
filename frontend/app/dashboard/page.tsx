// frontend/app/dashboard/page.tsx

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { campaignApi, metricsApi, agentApi, setupApi, gameStateApi } from '@/lib/api';
import MetricsVisualization from '@/components/MetricsVisualization';
import CampaignCard from '@/components/CampaignCard';
import CustomerSegments from '@/components/CustomerSegments';
import CampaignCalendar from '@/components/CampaignCalendar';
import GameController from '../../components/GameController';
import SetupInfoDisplay from '../../components/SetupInfoDisplay';
import SpendOptimizationChart from '../../components/SpendOptimizationChart';
import { Campaign, ChannelMetrics, CustomerSegment, Schedule, Company, Product } from '@/lib/types';

export default function Dashboard() {
  const router = useRouter();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [channelMetrics, setChannelMetrics] = useState<ChannelMetrics[]>([]);
  const [segments, setSegments] = useState<CustomerSegment[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [company, setCompany] = useState<Company | null>(null);
  const [product, setProduct] = useState<Product | null>(null);
  const [optimizationData, setOptimizationData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [gameDate, setGameDate] = useState(new Date());
  const [showSetupIncomplete, setShowSetupIncomplete] = useState(false);

  useEffect(() => {
    checkSetupAndLoadData();
  }, []);

  const checkSetupAndLoadData = async () => {
    try {
      // First check if setup is complete
      const setup = await setupApi.getCurrent();
      
      if (!setup || !setup.is_active) {
        // No setup or inactive, redirect to home for wizard
        router.push('/');
        return;
      }
      
      // Check if setup has all required fields
      if (!setup.company_id || !setup.product_id || !setup.monthly_budget) {
        setShowSetupIncomplete(true);
        setLoading(false);
        return;
      }
      
      // Setup is complete, load dashboard data
      await loadDashboardData(setup);
      
    } catch (error) {
      console.error('Error checking setup:', error);
      // On error, redirect to setup wizard
      router.push('/');
    }
  };

  const loadDashboardData = async (setup: any) => {
    try {
      // Load company and product info
      if (setup.company_id && setup.product_id) {
        const [companies, products] = await Promise.all([
          setupApi.getCompanies(),
          setupApi.getProducts()
        ]);
        
        const currentCompany = companies.find((c: any) => c.id === setup.company_id);
        const currentProduct = products.find((p: any) => p.id === setup.product_id);
        
        setCompany(currentCompany);
        setProduct(currentProduct);
      }

      // Load other dashboard data in parallel
      const [campaignsData, metricsData, segmentsData, optimizationData] = await Promise.all([
        campaignApi.list({ status: 'active' }),
        metricsApi.getChannelMetrics(7),
        agentApi.getSegments(),
        gameStateApi.getOptimizationData(30) // Get real optimization data
      ]);

      setCampaigns(campaignsData);
      setChannelMetrics(metricsData);
      setSegments(segmentsData);
      
      // Process optimization data for the chart
      const processedOptData = optimizationData.map((item: any) => ({
        date: new Date(item.date),
        optimal: item.optimal,
        nonOptimal: item.nonOptimal
      }));
      
      setOptimizationData(processedOptData);
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCampaignUpdate = async () => {
    const updatedCampaigns = await campaignApi.list({ status: 'active' });
    setCampaigns(updatedCampaigns);
  };

  const handleDateChange = (date: Date) => {
    setGameDate(date);
    // Optionally reload optimization data when date changes
    refreshOptimizationData();
  };

  const refreshOptimizationData = async () => {
    try {
      const optimizationData = await gameStateApi.getOptimizationData(30);
      const processedOptData = optimizationData.map((item: any) => ({
        date: new Date(item.date),
        optimal: item.optimal,
        nonOptimal: item.nonOptimal
      }));
      setOptimizationData(processedOptData);
    } catch (error) {
      console.error('Error refreshing optimization data:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (showSetupIncomplete) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Setup Incomplete</h2>
          <p className="text-gray-600 mb-4">Please complete the setup wizard to continue.</p>
          <button
            onClick={() => router.push('/')}
            className="btn-primary"
          >
            Complete Setup
          </button>
        </div>
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
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Optimization Performance</h2>
            <button
              onClick={refreshOptimizationData}
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              Refresh Data
            </button>
          </div>
          <SpendOptimizationChart data={optimizationData} />
          {optimizationData.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <p>No optimization data available yet.</p>
              <p className="text-sm mt-2">Run campaigns to see performance metrics.</p>
            </div>
          )}
        </div>
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
              await refreshOptimizationData();
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
          <button
            onClick={() => router.push('/')}
            className="btn-outline"
          >
            Run Setup Wizard
          </button>
        </div>
      </div>
    </div>
  );
}