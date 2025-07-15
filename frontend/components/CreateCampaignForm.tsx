// components/CreateCampaignForm.tsx
import { useState } from 'react';
import { toast } from 'react-hot-toast';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { FaSave, FaTimes } from 'react-icons/fa';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Segment {
  id: number;
  name: string;
  description: string;
}

interface CreateCampaignFormProps {
  segments: Segment[];
  onCancel: () => void;
}

interface CampaignFormData {
  name: string;
  description: string;
  channel: string;
  segment_id: number;
  frequency_days: number;
  assigned_budget: number;
  theme: string;
  strategy: string;
}

export default function CreateCampaignForm({ segments, onCancel }: CreateCampaignFormProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<CampaignFormData>({
    name: '',
    description: '',
    channel: 'facebook',
    segment_id: segments.length > 0 ? segments[0].id : 0,
    frequency_days: 7,
    assigned_budget: 1000,
    theme: '',
    strategy: ''
  });

  const channels = [
    { value: 'facebook', label: 'Facebook', color: 'text-blue-600' },
    { value: 'email', label: 'Email', color: 'text-green-600' },
    { value: 'google_ads', label: 'Google Ads', color: 'text-red-600' }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.name || !formData.description) {
      toast.error('Please fill in all required fields');
      return;
    }

    if (formData.assigned_budget < 100) {
      toast.error('Budget must be at least $100');
      return;
    }

    try {
      setLoading(true);
      
      // Create campaign
      const response = await axios.post(`${API_BASE}/api/campaigns/`, formData);
      
      toast.success('Campaign created successfully!');
      router.push('/dashboard');
    } catch (error) {
      console.error('Error creating campaign:', error);
      toast.error('Failed to create campaign');
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field: keyof CampaignFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Create New Campaign</h2>
      
      <div className="space-y-6">
        {/* Campaign Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Campaign Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => updateField('name', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="e.g., Summer Sale 2024"
            required
          />
        </div>

        {/* Campaign Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description <span className="text-red-500">*</span>
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => updateField('description', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            rows={3}
            placeholder="Describe the campaign goals and key messages..."
            required
          />
        </div>

        {/* Channel Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Marketing Channel <span className="text-red-500">*</span>
          </label>
          <div className="grid grid-cols-3 gap-3">
            {channels.map(channel => (
              <button
                key={channel.value}
                type="button"
                onClick={() => updateField('channel', channel.value)}
                className={`p-3 border-2 rounded-lg text-center transition-all ${
                  formData.channel === channel.value
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <span className={`font-medium ${channel.color}`}>{channel.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Customer Segment */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Target Segment <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.segment_id}
            onChange={(e) => updateField('segment_id', parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            required
          >
            {segments.map(segment => (
              <option key={segment.id} value={segment.id}>
                {segment.name} - {segment.description}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {/* Publishing Frequency */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Publishing Frequency (days) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              value={formData.frequency_days}
              onChange={(e) => updateField('frequency_days', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              min="1"
              max="30"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              How often to publish new content
            </p>
          </div>

          {/* Budget */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Monthly Budget ($) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              value={formData.assigned_budget}
              onChange={(e) => updateField('assigned_budget', parseFloat(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              min="100"
              step="50"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Initial budget allocation
            </p>
          </div>
        </div>

        {/* Campaign Theme */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Campaign Theme
          </label>
          <input
            type="text"
            value={formData.theme}
            onChange={(e) => updateField('theme', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="e.g., Summer Vibes, Back to School, Holiday Special"
          />
        </div>

        {/* Strategy */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Strategy & Notes
          </label>
          <textarea
            value={formData.strategy}
            onChange={(e) => updateField('strategy', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            rows={2}
            placeholder="Additional strategic notes or special instructions..."
          />
        </div>
      </div>

      {/* Form Actions */}
      <div className="mt-8 flex justify-end space-x-4">
        <button
          type="button"
          onClick={onCancel}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
        >
          <FaTimes className="mr-2" />
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Creating...
            </>
          ) : (
            <>
              <FaSave className="mr-2" />
              Create Campaign
            </>
          )}
        </button>
      </div>
    </form>
  );
}