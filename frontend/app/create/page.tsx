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
      router.push('/dashboard');
    } catch (error) {
      console.error('Error creating campaign:', error);
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
          <h2 className="text-xl font-semibold mb-4">Generate Campaign Ideas</h2>
          <p className="text-gray-600 mb-6">
            Our AI will analyze your customer segments and create tailored campaign ideas across all channels.
          </p>
          
          <div className="mb-6">
            <h3 className="font-medium text-gray-900 mb-2">Available Segments:</h3>
            <div className="flex flex-wrap gap-2">
              {segments.map((segment) => (
                <span
                  key={segment.id}
                  className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
                >
                  {segment.name}
                </span>
              ))}
            </div>
          </div>

          <div className="flex gap-4">
            <button
              onClick={handleGenerateIdeas}
              disabled={loading || segments.length === 0}
              className="btn-primary"
            >
              {loading ? 'Generating...' : 'Generate Ideas'}
            </button>
            <button
              onClick={() => setStep('customize')}
              className="btn-outline"
            >
              Create Custom Campaign
            </button>
          </div>
        </div>
      )}

      {step === 'select' && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Select a Campaign Idea</h2>
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
          
          <div className="mt-6">
            <button
              onClick={() => setStep('generate')}
              className="btn-outline"
            >
              Back
            </button>
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
          onCancel={() => setStep(selectedIdea ? 'select' : 'generate')}
        />
      )}
    </div>
  );
}