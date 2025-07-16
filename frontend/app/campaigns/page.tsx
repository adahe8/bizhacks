// frontend/app/campaigns/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { campaignApi } from '@/lib/api';
import { Campaign, ContentAsset } from '@/lib/types';
import { format } from 'date-fns';

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [expandedCampaigns, setExpandedCampaigns] = useState<Set<string>>(new Set());
  const [campaignContent, setCampaignContent] = useState<Record<string, ContentAsset[]>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    try {
      const data = await campaignApi.list();
      setCampaigns(data);
    } catch (error) {
      console.error('Error loading campaigns:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleCampaignExpansion = async (campaignId: string) => {
    const newExpanded = new Set(expandedCampaigns);
    
    if (newExpanded.has(campaignId)) {
      newExpanded.delete(campaignId);
    } else {
      newExpanded.add(campaignId);
      
      // Load content if not already loaded
      if (!campaignContent[campaignId]) {
        try {
          const content = await campaignApi.getContent(campaignId);
          setCampaignContent(prev => ({ ...prev, [campaignId]: content }));
        } catch (error) {
          console.error('Error loading campaign content:', error);
        }
      }
    }
    
    setExpandedCampaigns(newExpanded);
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'facebook': return '📱';
      case 'email': return '✉️';
      case 'google_seo': return '🔍';
      default: return '📢';
    }
  };

  const getStatusBadge = (status: string) => {
    const statusStyles = {
      active: 'bg-green-100 text-green-800',
      paused: 'bg-yellow-100 text-yellow-800',
      draft: 'bg-gray-100 text-gray-800',
      completed: 'bg-blue-100 text-blue-800'
    };
    
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusStyles[status as keyof typeof statusStyles] || statusStyles.draft}`}>
        {status}
      </span>
    );
  };

  const renderContent = (content: ContentAsset) => {
    const contentData = content.copy_text ? JSON.parse(content.copy_text) : {};
    
    return (
      <div key={content.id} className="border rounded-lg p-4 mb-3">
        <div className="flex items-start justify-between mb-2">
          <div>
            <p className="text-sm font-medium text-gray-900">
              {content.platform?.toUpperCase()} Content
            </p>
            <p className="text-xs text-gray-500">
              {content.published_at ? format(new Date(content.published_at), 'PPpp') : 'Not published'}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            {content.status === 'published' ? (
              <span className="text-green-600">✓ Published</span>
            ) : (
              <span className="text-red-600">✗ Not Published</span>
            )}
          </div>
        </div>
        
        <div className="bg-gray-50 rounded p-3 text-sm">
          {content.platform === 'email' && (
            <div>
              <p className="font-medium">Subject: {contentData.subject_line || 'N/A'}</p>
              <p className="text-gray-600 mt-1">Preview: {contentData.preview_text || 'N/A'}</p>
            </div>
          )}
          
          {content.platform === 'facebook' && (
            <div>
              <p className="text-gray-700">{contentData.primary_text || 'N/A'}</p>
              {contentData.hashtags && (
                <p className="text-blue-600 mt-2">{contentData.hashtags.join(' ')}</p>
              )}
            </div>
          )}
          
          {content.platform === 'google_seo' && (
            <div>
              <p className="font-medium">Keywords:</p>
              <p className="text-gray-600">
                {contentData.ads_content?.keywords?.join(', ') || 'N/A'}
              </p>
            </div>
          )}
        </div>
      </div>
    );
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
        <h1 className="text-3xl font-bold text-gray-900">All Campaigns</h1>
        <p className="text-gray-600 mt-2">View and manage all your marketing campaigns</p>
      </div>

      <div className="space-y-4">
        {campaigns.map((campaign) => (
          <div key={campaign.id} className="card">
            <div 
              className="cursor-pointer"
              onClick={() => toggleCampaignExpansion(campaign.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <span className="text-2xl">{getChannelIcon(campaign.channel)}</span>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{campaign.name}</h3>
                    <p className="text-sm text-gray-600">{campaign.description}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Budget</p>
                    <p className="font-medium">${campaign.budget}/month</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Segment</p>
                    <p className="font-medium">{campaign.customer_segment || 'All'}</p>
                  </div>
                  {getStatusBadge(campaign.status)}
                  <span className={`transform transition-transform ${expandedCampaigns.has(campaign.id) ? 'rotate-180' : ''}`}>
                    ▼
                  </span>
                </div>
              </div>
            </div>
            
            {expandedCampaigns.has(campaign.id) && (
              <div className="mt-6 pt-6 border-t">
                <h4 className="font-medium text-gray-900 mb-4">Campaign Content</h4>
                {campaignContent[campaign.id] ? (
                  campaignContent[campaign.id].length > 0 ? (
                    campaignContent[campaign.id].map(renderContent)
                  ) : (
                    <p className="text-gray-500">No content generated yet</p>
                  )
                ) : (
                  <div className="flex justify-center py-4">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
        
        {campaigns.length === 0 && (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <p className="text-gray-500">No campaigns created yet.</p>
            <a href="/create" className="text-primary-600 hover:text-primary-700 mt-2 inline-block">
              Create your first campaign →
            </a>
          </div>
        )}
      </div>
    </div>
  );
}