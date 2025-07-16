// frontend/components/modals/AICampaignGenerationModal.tsx

import { useState, useEffect } from 'react';
import { agentApi, campaignApi, setupApi } from '@/lib/api';
import { CampaignIdea, SetupConfig } from '@/lib/types';

interface Props {
  segments: any[];
  channels: string[];
  onComplete: () => void;
}

export default function AICampaignGenerationModal({ segments, channels, onComplete }: Props) {
  const [isGenerating, setIsGenerating] = useState(true);
  const [campaignIdeas, setCampaignIdeas] = useState<CampaignIdea[]>([]);
  const [selectedCampaigns, setSelectedCampaigns] = useState<Set<number>>(new Set());
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [setup, setSetup] = useState<SetupConfig | null>(null);

  useEffect(() => {
    loadSetupAndGenerateIdeas();
  }, []);

  const loadSetupAndGenerateIdeas = async () => {
    try {
      // First fetch the current setup to get product_id
      const currentSetup = await setupApi.getCurrent();
      if (!currentSetup) {
        setError('No active setup found. Please complete the setup wizard.');
        setIsGenerating(false);
        return;
      }
      setSetup(currentSetup);
      
      // Then generate campaign ideas
      await generateCampaignIdeas();
    } catch (error) {
      console.error('Error loading setup:', error);
      setError('Failed to load setup configuration.');
      setIsGenerating(false);
    }
  };

  const generateCampaignIdeas = async () => {
    try {
      setIsGenerating(true);
      setError(null);
      
      if (!setup) {
        setError('Setup not loaded. Please try again.');
        setIsGenerating(false);
        return;
      }
      
      const segmentNames = segments.map(s => s.name);
      const ideas = await agentApi.generateCampaignIdeas({
        segments: segmentNames,
        channels: channels
      });
      
      setCampaignIdeas(ideas);
      // Pre-select all campaigns by default
      setSelectedCampaigns(new Set(ideas.map((_, index) => index)));
    } catch (error) {
      console.error('Error generating campaign ideas:', error);
      setError('Failed to generate campaign ideas. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const toggleCampaignSelection = (index: number) => {
    const newSelection = new Set(selectedCampaigns);
    if (newSelection.has(index)) {
      newSelection.delete(index);
    } else {
      newSelection.add(index);
    }
    setSelectedCampaigns(newSelection);
  };

  const createSelectedCampaigns = async () => {
    if (selectedCampaigns.size === 0) {
      alert('Please select at least one campaign to create.');
      return;
    }

    if (!setup || !setup.product_id) {
      alert('No product selected. Please complete the setup wizard.');
      return;
    }

    setIsCreating(true);
    
    try {
      // Create selected campaigns
      const campaignsToCreate = Array.from(selectedCampaigns).map(index => campaignIdeas[index]);
      
      for (const campaign of campaignsToCreate) {
        await campaignApi.create({
          name: campaign.name,
          description: campaign.description,
          channel: campaign.channel,
          customer_segment: campaign.customer_segment,
          frequency: campaign.frequency || 'weekly',
          budget: campaign.suggested_budget,
          product_id: setup.product_id // Use product_id from setup
        });
      }
      
      // Budget reallocation will happen automatically after campaigns are added
      // as per the requirement
      
      onComplete();
    } catch (error) {
      console.error('Error creating campaigns:', error);
      setError('Failed to create campaigns. Please try again.');
    } finally {
      setIsCreating(false);
    }
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'facebook': return '📱';
      case 'email': return '✉️';
      case 'google_seo': return '🔍';
      default: return '📢';
    }
  };

  const getChannelColor = (channel: string) => {
    switch (channel) {
      case 'facebook': return 'bg-blue-50 border-blue-200';
      case 'email': return 'bg-purple-50 border-purple-200';
      case 'google_seo': return 'bg-green-50 border-green-200';
      default: return 'bg-gray-50 border-gray-200';
    }
  };

  if (isGenerating) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-white rounded-lg p-8 max-w-md w-full text-center shadow-lg">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Creating Campaign Ideas...</h2>
          <p className="text-gray-600">Our AI is generating personalized campaigns for your segments</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg">
          {/* Header */}
          <div className="p-6 border-b">
            <h2 className="text-2xl font-bold text-gray-900">AI-Generated Campaign Ideas</h2>
            <p className="text-gray-600 mt-2">
              Select the campaigns you'd like to create. You can choose multiple campaigns across different channels.
            </p>
            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
                {error}
              </div>
            )}
          </div>

          {/* Campaign Grid */}
          <div className="p-6">
            <div className="mb-4 flex justify-between items-center">
              <div>
                <span className="text-sm text-gray-500">
                  {selectedCampaigns.size} of {campaignIdeas.length} campaigns selected
                </span>
              </div>
              <div className="space-x-2">
                <button
                  onClick={() => setSelectedCampaigns(new Set(campaignIdeas.map((_, i) => i)))}
                  className="text-sm text-primary-600 hover:text-primary-700"
                >
                  Select All
                </button>
                <span className="text-gray-400">|</span>
                <button
                  onClick={() => setSelectedCampaigns(new Set())}
                  className="text-sm text-primary-600 hover:text-primary-700"
                >
                  Deselect All
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {campaignIdeas.map((campaign, index) => (
                <div
                  key={index}
                  className={`
                    border-2 rounded-lg p-4 cursor-pointer transition-all
                    ${selectedCampaigns.has(index) 
                      ? 'border-primary-500 bg-primary-50' 
                      : `border-gray-200 hover:border-gray-300 ${getChannelColor(campaign.channel)}`
                    }
                  `}
                  onClick={() => toggleCampaignSelection(index)}
                >
                  {/* Selection Indicator */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedCampaigns.has(index)}
                        onChange={() => toggleCampaignSelection(index)}
                        className="h-5 w-5 text-primary-600 rounded border-gray-300 mr-3"
                        onClick={(e) => e.stopPropagation()}
                      />
                      <span className="text-2xl">{getChannelIcon(campaign.channel)}</span>
                    </div>
                    <span className="text-xs px-2 py-1 bg-white rounded-full capitalize">
                      {campaign.channel.replace('_', ' ')}
                    </span>
                  </div>

                  {/* Campaign Details */}
                  <h3 className="font-semibold text-gray-900 mb-2">{campaign.name}</h3>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">{campaign.description}</p>
                  
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Segment:</span>
                      <span className="font-medium">{campaign.customer_segment}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Frequency:</span>
                      <span className="font-medium capitalize">{campaign.frequency}</span>
                    </div>
                    {campaign.objectives && (
                      <div className="pt-2 border-t">
                        <p className="text-gray-700 italic">
                          Goal: {campaign.objectives.primary_goal}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Budget Note */}
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> Budget allocation will be automatically optimized across selected campaigns after creation.
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="p-6 border-t bg-gray-50">
            <div className="flex justify-between items-center">
              <button
                onClick={() => generateCampaignIdeas()}
                className="btn-outline"
                disabled={isGenerating || isCreating || !setup}
              >
                Regenerate Ideas
              </button>
              <button
                onClick={createSelectedCampaigns}
                disabled={selectedCampaigns.size === 0 || isCreating || !setup}
                className="btn-primary"
              >
                {isCreating ? (
                  <>
                    <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white inline-block mr-2"></span>
                    Creating Campaigns...
                  </>
                ) : (
                  `Create ${selectedCampaigns.size} Campaign${selectedCampaigns.size !== 1 ? 's' : ''}`
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}