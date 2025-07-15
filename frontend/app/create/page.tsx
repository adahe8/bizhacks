'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import CreateCampaignForm from '@/components/CreateCampaignForm';
import { agentApi, campaignApi } from '@/lib/api';
import { CustomerSegment, CampaignIdea } from '@/lib/types';

export default function CreateCampaign() {
  const router = useRouter();
  const [segments, setSegments] = useState<CustomerSegment[]>([]);
  const [campaignIdeas, setCampaignIdeas] = useState<CampaignIdea[]>([]);
  const [selectedIdea, setSelectedIdea] = useState<CampaignIdea | null>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<'generate' | 'select' | 'customize'>('generate');

  useEffect(() => {
    loadSegments();
  }, []);

  const loadSegments = async () => {
    try {
      const segmentsData = await agentApi.getSegments();
      setSegments(segmentsData);
    } catch (error) {
      console.error('Error loading segments:', error);
    }
  };

  const handleGenerateIdeas = async () => {
    if (segments.length === 0) {
      alert('No customer segments available. Please generate segments first.');
      return;
    }

    setLoading(true);
    try {
      const ideas = await agentApi.generateCampaignIdeas({
        segments: segments.map(s => s.name),
        channels: ['facebook', 'email', 'google_seo'],
      });
      setCampaignIdeas(ideas);
      setStep('select');
    } catch (error) {
      console.error('Error generating ideas:', error);
      alert('Failed to generate campaign ideas. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectIdea = (idea: CampaignIdea) => {
    setSelectedIdea(idea);
    setStep('customize');
  };

  const handleCreateCampaign = async (campaignData: any) => {
    try {
      const campaign = await campaignApi.create(campaignData);
      router.push('/campaigns');
    } catch (error) {
      console.error('Error creating campaign:', error);
      alert('Failed to create campaign. Please try again.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Create Campaign</h1>
        <p className="text-gray-600 mt-2">Generate AI-powered campaign ideas or create custom campaigns</p>
      </div>

      {step === 'generate' && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Campaign Creation Options</h2>
          <p className="text-gray-600 mb-6">
            Choose how you want to create your campaign.
          </p>
          
          <div className="mb-6">
            <h3 className="font-medium text-gray-900 mb-2">Available Segments:</h3>
            {segments.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {segments.map((segment) => (
                  <span
                    key={segment.id}
                    className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
                  >
                    {segment.name} ({segment.size}%)
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No segments available. Generate segments from the dashboard first.</p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={handleGenerateIdeas}
              disabled={loading || segments.length === 0}
              className={`p-6 border-2 rounded-lg text-center transition-all ${
                loading || segments.length === 0
                  ? 'border-gray-200 bg-gray-50 cursor-not-allowed'
                  : 'border-primary-200 hover:border-primary-400 hover:bg-primary-50 cursor-pointer'
              }`}
            >
              <div className="text-3xl mb-3">🤖</div>
              <h3 className="font-semibold text-lg mb-2">AI-Generated Ideas</h3>
              <p className="text-sm text-gray-600">
                Let AI create campaign ideas based on your segments and goals
              </p>
              {loading && <p className="text-sm text-primary-600 mt-2">Generating ideas...</p>}
            </button>
            
            <button
              onClick={() => setStep('customize')}
              className="p-6 border-2 rounded-lg text-center transition-all border-gray-200 hover:border-gray-400 hover:bg-gray-50 cursor-pointer"
            >
              <div className="text-3xl mb-3">✏️</div>
              <h3 className="font-semibold text-lg mb-2">Create Custom</h3>
              <p className="text-sm text-gray-600">
                Manually create a campaign with your own specifications
              </p>
            </button>
          </div>
        </div>
      )}

      {step === 'select' && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Select a Campaign Idea</h2>
            <button
              onClick={() => setStep('generate')}
              className="text-gray-600 hover:text-gray-900"
            >
              ← Back
            </button>
          </div>
          
          <div className="space-y-4">
            {campaignIdeas.map((idea, index) => (
              <div
                key={index}
                className="card hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleSelectIdea(idea)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">{idea.name}</h3>
                    <p className="text-gray-600 mt-1">{idea.description}</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <span className="text-sm px-2 py-1 bg-gray-100 rounded">
                        {idea.channel}
                      </span>
                      <span className="text-sm px-2 py-1 bg-gray-100 rounded">
                        {idea.customer_segment}
                      </span>
                      <span className="text-sm px-2 py-1 bg-gray-100 rounded">
                        {idea.frequency}
                      </span>
                    </div>
                  </div>
                  <div className="ml-4 text-right">
                    <p className="text-2xl font-bold text-primary-600">
                      ${idea.suggested_budget.toFixed(0)}
                    </p>
                    <p className="text-sm text-gray-500">per month</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {step === 'customize' && (
        <CreateCampaignForm
          initialData={selectedIdea ? {
            name: selectedIdea.name,
            description: selectedIdea.description,
            channel: selectedIdea.channel as any,
            customer_segment: selectedIdea.customer_segment,
            frequency: selectedIdea.frequency as any,
            budget: selectedIdea.suggested_budget,
          } : undefined}
          onSubmit={handleCreateCampaign}
          onCancel={() => {
            setSelectedIdea(null);
            setStep(selectedIdea ? 'select' : 'generate');
          }}
        />
      )}
    </div>
  );
}