// app/dashboard/page.tsx
"use client";

import { useState, useEffect } from "react";
import { toast } from "react-hot-toast";
import axios from "axios";
import {
  FaFacebook,
  FaEnvelope,
  FaGoogle,
  FaChartLine,
  FaPlus,
  FaPlay,
  FaPause,
  FaUsers,
} from "react-icons/fa";
import SetupModals from "@/components/SetupModals";
import CampaignCard from "@/components/CampaignCard";
import MetricsVisualization from "@/components/MetricsVisualization";
import CustomerSegments from "@/components/CustomerSegments";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Campaign {
  id: number;
  name: string;
  description: string;
  channel: string;
  status: string;
  assigned_budget: number;
  current_budget: number;
  frequency_days: number;
  segment: {
    name: string;
  };
}

interface Metrics {
  channel: string;
  impressions: number;
  clicks: number;
  conversions: number;
  spend: number;
  roi: number;
}

interface Segment {
  id: number;
  name: string;
  description: string;
  size_estimate: number;
}

export default function Dashboard() {
  const [isFirstVisit, setIsFirstVisit] = useState(false);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [metrics, setMetrics] = useState<Metrics[]>([]);
  const [segments, setSegments] = useState<Segment[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    checkSetupAndLoadData();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const checkSetupAndLoadData = async () => {
    try {
      // Check if company is setup
      const response = await axios.get(`${API_BASE}/api/campaigns/`);
      if (response.data.length === 0) {
        // Check if this is truly first visit by checking company setup
        try {
          await axios.get(`${API_BASE}/api/company/details`);
        } catch (error: any) {
          if (error.response?.status === 404) {
            setIsFirstVisit(true);
          }
        }
      }

      // Load data
      await Promise.all([loadCampaigns(), loadMetrics(), loadSegments()]);
    } catch (error) {
      console.error("Error checking setup:", error);
      toast.error("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const loadCampaigns = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/campaigns/`);
      setCampaigns(response.data);
    } catch (error) {
      console.error("Error loading campaigns:", error);
    }
  };

  const loadMetrics = async () => {
    try {
      // Mock metrics for now
      const mockMetrics: Metrics[] = [
        {
          channel: "facebook",
          impressions: 125000,
          clicks: 3750,
          conversions: 187,
          spend: 1250,
          roi: 2.4,
        },
        {
          channel: "email",
          impressions: 50000,
          clicks: 2500,
          conversions: 250,
          spend: 500,
          roi: 5.2,
        },
        {
          channel: "google_ads",
          impressions: 200000,
          clicks: 4000,
          conversions: 320,
          spend: 2000,
          roi: 3.1,
        },
      ];
      setMetrics(mockMetrics);
    } catch (error) {
      console.error("Error loading metrics:", error);
    }
  };

  const loadSegments = async () => {
    try {
      // Mock segments for now
      const mockSegments: Segment[] = [
        {
          id: 1,
          name: "Young Professionals",
          description: "Age 25-35, urban, high disposable income",
          size_estimate: 15000,
        },
        {
          id: 2,
          name: "Family Oriented",
          description: "Parents with children, suburban",
          size_estimate: 25000,
        },
        {
          id: 3,
          name: "Health Conscious",
          description: "Fitness enthusiasts, organic buyers",
          size_estimate: 12000,
        },
      ];
      setSegments(mockSegments);
    } catch (error) {
      console.error("Error loading segments:", error);
    }
  };

  const handleSetupComplete = async () => {
    setIsFirstVisit(false);
    toast.success("Setup completed successfully!");
    await checkSetupAndLoadData();
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await checkSetupAndLoadData();
    setRefreshing(false);
    toast.success("Dashboard refreshed");
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case "facebook":
        return <FaFacebook className="text-blue-600" />;
      case "email":
        return <FaEnvelope className="text-green-600" />;
      case "google_ads":
        return <FaGoogle className="text-red-600" />;
      default:
        return null;
    }
  };

  const getChannelMetrics = (channel: string) => {
    return metrics.find((m) => m.channel === channel) || null;
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
      {/* Setup Modals for First Visit */}
      {isFirstVisit && <SetupModals onComplete={handleSetupComplete} />}

      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              Marketing Campaign Dashboard
            </h1>
            <div className="flex space-x-4">
              <button
                onClick={() => (window.location.href = "/create")}
                className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                <FaPlus className="mr-2" />
                New Campaign
              </button>
              <button
                onClick={handleRefresh}
                className={`inline-flex items-center px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 ${
                  refreshing ? "opacity-50 cursor-not-allowed" : ""
                }`}
                disabled={refreshing}
              >
                <FaChartLine className="mr-2" />
                {refreshing ? "Refreshing..." : "Refresh"}
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Metrics Overview */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Channel Performance Overview
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {["facebook", "email", "google_ads"].map((channel) => {
              const channelMetrics = getChannelMetrics(channel);
              return (
                <div key={channel} className="bg-white rounded-lg shadow p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center">
                      {getChannelIcon(channel)}
                      <h3 className="ml-2 text-lg font-medium capitalize">
                        {channel.replace("_", " ")}
                      </h3>
                    </div>
                  </div>
                  {channelMetrics && (
                    <MetricsVisualization metrics={channelMetrics} />
                  )}
                </div>
              );
            })}
          </div>
        </section>

        {/* Customer Segments */}
        <section className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Customer Segments
            </h2>
            <button
              onClick={() =>
                toast("Segment analysis in progress...", {
                  icon: "📊",
                  duration: 3000,
                })
              }
              className="text-indigo-600 hover:text-indigo-800 flex items-center"
            >
              <FaUsers className="mr-2" />
              Analyze Segments
            </button>
          </div>
          <CustomerSegments segments={segments} />
        </section>

        {/* Running Campaigns */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Active Campaigns (
            {campaigns.filter((c) => c.status === "running").length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {campaigns.length === 0 ? (
              <div className="col-span-full text-center py-12 bg-white rounded-lg shadow">
                <p className="text-gray-500 mb-4">No campaigns yet</p>
                <button
                  onClick={() => (window.location.href = "/create")}
                  className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                >
                  <FaPlus className="mr-2" />
                  Create Your First Campaign
                </button>
              </div>
            ) : (
              campaigns.map((campaign) => (
                <CampaignCard
                  key={campaign.id}
                  campaign={campaign}
                  onUpdate={loadCampaigns}
                />
              ))
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
