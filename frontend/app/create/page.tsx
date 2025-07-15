// app/create/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { 
  FaArrowLeft, 
  FaRobot, 
  FaPlus,
  FaFacebook,
  FaEnvelope,
  FaGoogle
} from 'react-icons/fa';
import CreateCampaignForm from '@/components/CreateCampaignForm';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Segment {
  id: number;
  name: string;
  description: string;
}

interface GeneratedCampaign {
  id: string;
  name: string;
  description: string;
  channel: string;
  segment_id: number;
  frequency_days: number;
  budget: number;
  theme?: string;
  strategy?: string;
  selected: boolean;
}

export default function CreateCampaignPage() {
  const router = useRouter();
  const [mode, setMode] = useState<'manual' | 'ai' | null>(null);
  const [segments, setSegments] = useState<Segment[]>([]);
  const [selectedSegments, setSelectedSegments] = useState<number[]>([]);
  const [generatedCampaigns, setGeneratedCampaigns] = useState<GeneratedCampaign[]>([]);
  const [loading, setLoading] = useState(false);
  const [campaignsPerSegment, setCampaignsPerSegment] = useState(3);

  useEffect(() => {
    loadSegments();
  }, []);

  const loadSegments = async () => {
    try {
      // Mock segments for now
      const mockSegments: Segment[] = [
        {
          id: 1,
          name: 'Young Professionals',
          description: 'Age 25-35, urban, high disposable income'
        },
        {
          id: 2,
          name: 'Family Oriented',
          description: 'Parents with children, suburban'
        },
        {
          id: 3,
          name: 'Health Conscious',
          description: 'Fitness enthusiasts, organic buyers'
        }
      ];
      setSegments(mockSegments);
    } catch (error) {
      console.error('Error loading segments:', error);
      toast.error('Failed to load customer segments');
    }
  };

  const handleAIGeneration = async () => {
    if (selectedSegments.length === 0) {
      toast.error('Please select at least one customer segment');
      return;
    }

    try {
      setLoading(true);
      
      // Call AI generation endpoint
      const response = await axios.post(`${API_BASE}/api/agents/generate-campaigns`, {
        segment_ids: selectedSegments,
        campaigns_per_segment: campaignsPerSegment
      });

      // Simulate AI-generated campaigns
      const mockGeneratedCampaigns: GeneratedCampaign[] = [];
      const channels = ['facebook', 'email', 'google_ads'];
      const themes = ['Summer Sale', 'Product Launch', 'Brand Awareness', 'Customer Retention'];
      
      selectedSegments.forEach(segmentId => {
        const segment = segments.find(s => s.id === segmentId);
        if (segment) {
          for (let i = 0; i < campaignsPerSegment; i++) {
            const channel = channels[i % channels.length];
            const theme = themes[Math.floor(Math.random() * themes.length)];
            
            mockGeneratedCampaigns.push({
              id: `gen_${segmentId}_${i}`,
              name: `${theme} - ${segment.name} (${channel})`,
              description: `AI-generated campaign targeting ${segment.name} segment with ${theme} messaging on ${channel} platform`,
              channel,
              segment_id: segmentId,
              frequency_days: channel === 'email' ? 7 : 3,
              budget: Math.floor(Math.random() * 1000) + 500,
              theme,
              strategy: `Focus on ${segment.description} with compelling ${theme} content`,
              selected: true
            });
          }
        }
      });

      setGeneratedCampaigns(mockGeneratedCampaigns);
      toast.success('AI campaigns generated successfully!');
    } catch (error) {
      console.error('Error generating campaigns:', error);
      toast.error('Failed to generate campaigns');
    } finally {
      setLoading(false);
    }
  };

  const toggleCampaignSelection = (campaignId: string) => {
    setGeneratedCampaigns(prev =>
      prev.map(camp =>
        camp.id === campaignId ? { ...camp, selected: !camp.selected } : camp
      )
    );
  };

  const handleApproveSelected = async () => {
    const selectedCampaigns = generatedCampaigns.filter(c => c.selected);
    
    if (selectedCampaigns.length === 0) {
      toast.error('Please select at least one campaign to approve');
      return;
    }

    try {
      setLoading(true);
      
      // Create campaigns
      for (const campaign of selectedCampaigns) {
        await axios.post(`${API_BASE}/api/campaigns/`, {
          name: campaign.name,
          description: campaign.description,
          channel: campaign.channel,
          segment_id: campaign.segment_id,
          frequency_days: campaign.frequency_days,
          assigned_budget: campaign.budget,
          theme: campaign.theme,
          strategy: campaign.strategy
        });
      }

      toast.success(`Created ${selectedCampaigns.length} campaigns successfully!`);
      router.push('/dashboard');
    } catch (error) {
      console.error('Error creating campaigns:', error);
      toast.error('Failed to create campaigns');
    } finally {
      setLoading(false);
    }
  };

  const getChannelIcon = (channel: string) => {
    switch(channel) {
      case 'facebook':
        return <FaFacebook className="text-blue-600" />;
      case 'email':
        return <FaEnvelope className="text-green-600" />;
      case 'google_ads':
        return <FaGoogle className="text-red-600" />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center">
            <button
              onClick={() => router.push('/dashboard')}
              className="mr-4 p-2 text-gray-600 hover:text-gray-900"
            >
              <FaArrowLeft />
            </button>
            <h1 className="text-2xl font-bold text-gray-900">Create Campaign</h1>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {mode === null ? (
          // Mode Selection
          <div className="max-w-4xl mx-auto">
            <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">
              How would you like to create your campaigns?
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <button
                onClick={() => setMode('manual')}
                className="bg-white p-8 rounded-lg shadow-md hover:shadow-lg transition-shadow text-center group"
              >
                <FaPlus className="text-4xl text-indigo-600 mx-auto mb-4 group-hover:scale-110 transition-transform" />
                <h3 className="text-lg font-semibold mb-2">Manual Creation</h3>
                <p className="text-gray-600">
                  Create a single campaign with full control over all details
                </p>
              </button>
              
              <button
                onClick={() => setMode('ai')}
                className="bg-white p-8 rounded-lg shadow-md hover:shadow-lg transition-shadow text-center group"
              >
                <FaRobot className="text-4xl text-purple-600 mx-auto mb-4 group-hover:scale-110 transition-transform" />
                <h3 className="text-lg font-semibold mb-2">AI Generation</h3>
                <p className="text-gray-600">
                  Let AI generate multiple campaign ideas based on your segments
                </p>
              </button>
            </div>
          </div>
        ) : mode === 'manual' ? (
          // Manual Creation
          <div className="max-w-2xl mx-auto">
            <CreateCampaignForm segments={segments} onCancel={() => setMode(null)} />
          </div>
        ) : (
          // AI Generation
          <div>
            {generatedCampaigns.length === 0 ? (
              // Segment Selection
              <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">
                  Select Customer Segments
                </h2>
                
                <div className="space-y-3 mb-6">
                  {segments.map(segment => (
                    <label
                      key={segment.id}
                      className="flex items-start p-4 border rounded-lg cursor-pointer hover:bg-gray-50"
                    >
                      <input
                        type="checkbox"
                        checked={selectedSegments.includes(segment.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedSegments([...selectedSegments, segment.id]);
                          } else {
                            setSelectedSegments(selectedSegments.filter(id => id !== segment.id));
                          }
                        }}
                        className="mt-1 mr-3"
                      />
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{segment.name}</h4>
                        <p className="text-sm text-gray-600 mt-1">{segment.description}</p>
                      </div>
                    </label>
                  ))}
                </div>
                
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campaigns per segment
                  </label>
                  <input
                    type="number"
                    value={campaignsPerSegment}
                    onChange={(e) => setCampaignsPerSegment(parseInt(e.target.value))}
                    min="1"
                    max="5"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                
                <div className="flex justify-between">
                  <button
                    onClick={() => setMode(null)}
                    className="px-4 py-2 text-gray-700 hover:text-gray-900"
                  >
                    Back
                  </button>
                  <button
                    onClick={handleAIGeneration}
                    disabled={loading || selectedSegments.length === 0}
                    className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Generating...
                      </>
                    ) : (
                      <>
                        <FaRobot className="mr-2" />
                        Generate Campaigns
                      </>
                    )}
                  </button>
                </div>
              </div>
            ) : (
              // Generated Campaigns Review
              <div>
                <div className="mb-6 flex justify-between items-center">
                  <h2 className="text-xl font-semibold text-gray-900">
                    AI Generated Campaigns ({generatedCampaigns.filter(c => c.selected).length} selected)
                  </h2>
                  <button
                    onClick={() => {
                      setGeneratedCampaigns([]);
                      setSelectedSegments([]);
                    }}
                    className="text-gray-600 hover:text-gray-900"
                  >
                    Generate New
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                  {generatedCampaigns.map(campaign => (
                    <div
                      key={campaign.id}
                      className={`bg-white rounded-lg shadow p-4 cursor-pointer transition-all ${
                        campaign.selected
                          ? 'ring-2 ring-purple-500 shadow-lg'
                          : 'hover:shadow-md'
                      }`}
                      onClick={() => toggleCampaignSelection(campaign.id)}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center">
                          {getChannelIcon(campaign.channel)}
                          <h3 className="ml-2 font-medium text-gray-900 text-sm">
                            {campaign.name}
                          </h3>
                        </div>
                        <input
                          type="checkbox"
                          checked={campaign.selected}
                          onChange={() => {}}
                          className="mt-1"
                          onClick={(e) => e.stopPropagation()}
                        />
                      </div>
                      <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                        {campaign.description}
                      </p>
                      <div className="space-y-1 text-xs text-gray-500">
                        <p>Budget: ${campaign.budget}</p>
                        <p>Frequency: Every {campaign.frequency_days} days</p>
                        <p>Theme: {campaign.theme}</p>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="flex justify-center">
                  <button
                    onClick={handleApproveSelected}
                    disabled={loading || generatedCampaigns.filter(c => c.selected).length === 0}
                    className="inline-flex items-center px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 text-lg font-medium"
                  >
                    {loading ? 'Creating...' : `Create ${generatedCampaigns.filter(c => c.selected).length} Campaigns`}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}