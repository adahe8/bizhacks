// components/CampaignCard.tsx
import { useState } from 'react';
import { toast } from 'react-hot-toast';
import axios from 'axios';
import { 
  FaPlay, 
  FaPause, 
  FaEdit, 
  FaChartLine,
  FaDollarSign,
  FaCalendarAlt,
  FaUsers
} from 'react-icons/fa';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

interface CampaignCardProps {
  campaign: Campaign;
  onUpdate: () => void;
}

export default function CampaignCard({ campaign, onUpdate }: CampaignCardProps) {
  const [loading, setLoading] = useState(false);

  const getChannelColor = (channel: string) => {
    switch(channel) {
      case 'facebook':
        return 'bg-blue-100 text-blue-800';
      case 'email':
        return 'bg-green-100 text-green-800';
      case 'google_ads':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'running':
        return 'bg-green-100 text-green-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      case 'approved':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleToggleStatus = async () => {
    try {
      setLoading(true);
      
      if (campaign.status === 'running') {
        // Pause campaign
        await axios.delete(`${API_BASE}/api/schedules/${campaign.id}/schedule`);
        toast.success('Campaign paused');
      } else if (campaign.status === 'paused' || campaign.status === 'approved') {
        // Start/Resume campaign
        await axios.post(`${API_BASE}/api/schedules/${campaign.id}/schedule`, {
          frequency_days: campaign.frequency_days
        });
        toast.success('Campaign started');
      } else if (campaign.status === 'draft') {
        // Approve campaign first
        await axios.post(`${API_BASE}/api/campaigns/${campaign.id}/approve`);
        toast.success('Campaign approved! You can now start it.');
      }
      
      onUpdate();
    } catch (error) {
      console.error('Error toggling campaign status:', error);
      toast.error('Failed to update campaign status');
    } finally {
      setLoading(false);
    }
  };

  const handleViewMetrics = () => {
    // Navigate to detailed metrics view
    window.location.href = `/campaigns/${campaign.id}/metrics`;
  };

  const budgetUtilization = (campaign.current_budget / campaign.assigned_budget) * 100;

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200">
      <div className="p-6">
        {/* Header */}
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{campaign.name}</h3>
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">{campaign.description}</p>
          </div>
          <div className="flex flex-col items-end space-y-2">
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getChannelColor(campaign.channel)}`}>
              {campaign.channel.replace('_', ' ')}
            </span>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(campaign.status)}`}>
              {campaign.status}
            </span>
          </div>
        </div>

        {/* Metrics */}
        <div className="space-y-3 mb-4">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center text-gray-600">
              <FaUsers className="mr-2" />
              <span>Segment:</span>
            </div>
            <span className="font-medium text-gray-900">{campaign.segment.name}</span>
          </div>
          
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center text-gray-600">
              <FaCalendarAlt className="mr-2" />
              <span>Frequency:</span>
            </div>
            <span className="font-medium text-gray-900">Every {campaign.frequency_days} days</span>
          </div>
          
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center text-gray-600">
              <FaDollarSign className="mr-2" />
              <span>Budget:</span>
            </div>
            <span className="font-medium text-gray-900">
              ${campaign.current_budget.toFixed(0)} / ${campaign.assigned_budget.toFixed(0)}
            </span>
          </div>
          
          {/* Budget Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${Math.min(budgetUtilization, 100)}%` }}
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex space-x-2">
          <button
            onClick={handleToggleStatus}
            disabled={loading}
            className={`flex-1 inline-flex items-center justify-center px-3 py-2 border rounded-md text-sm font-medium transition-colors ${
              campaign.status === 'running'
                ? 'border-yellow-600 text-yellow-600 hover:bg-yellow-50'
                : 'border-green-600 text-green-600 hover:bg-green-50'
            } disabled:opacity-50`}
          >
            {campaign.status === 'running' ? (
              <>
                <FaPause className="mr-2" />
                Pause
              </>
            ) : (
              <>
                <FaPlay className="mr-2" />
                {campaign.status === 'draft' ? 'Approve' : 'Start'}
              </>
            )}
          </button>
          
          <button
            onClick={handleViewMetrics}
            className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <FaChartLine className="mr-2" />
            Metrics
          </button>
          
          <button
            onClick={() => window.location.href = `/campaigns/${campaign.id}/edit`}
            className="inline-flex items-center justify-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <FaEdit />
          </button>
        </div>
      </div>
    </div>
  );
}