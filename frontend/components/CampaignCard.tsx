import { Campaign } from '@/lib/types';
import { campaignApi, agentApi } from '@/lib/api';

interface Props {
  campaign: Campaign;
  onUpdate: () => void;
}

export default function CampaignCard({ campaign, onUpdate }: Props) {
  const handlePause = async () => {
    try {
      await campaignApi.pause(campaign.id);
      onUpdate();
    } catch (error) {
      console.error('Error pausing campaign:', error);
    }
  };

  const handleExecute = async () => {
    try {
      await agentApi.executeCampaign(campaign.id);
      alert('Campaign execution started');
    } catch (error) {
      console.error('Error executing campaign:', error);
    }
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'facebook':
        return '📱';
      case 'email':
        return '✉️';
      case 'google_seo':
        return '🔍';
      default:
        return '📢';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  return (
    <div className="card hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center">
          <span className="text-2xl mr-3">{getChannelIcon(campaign.channel)}</span>
          <div>
            <h3 className="font-semibold text-gray-900">{campaign.name}</h3>
            <p className="text-sm text-gray-500 capitalize">{campaign.channel}</p>
          </div>
        </div>
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(campaign.status)}`}>
          {campaign.status}
        </span>
      </div>

      <p className="text-sm text-gray-600 mb-4 line-clamp-2">
        {campaign.description || 'No description provided'}
      </p>

      <div className="space-y-2 mb-4">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Budget</span>
          <span className="font-medium">${campaign.budget.toFixed(0)}/month</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Frequency</span>
          <span className="font-medium capitalize">{campaign.frequency || 'Not set'}</span>
        </div>
        {campaign.customer_segment && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Segment</span>
            <span className="font-medium">{campaign.customer_segment}</span>
          </div>
        )}
      </div>

      <div className="flex gap-2">
        {campaign.status === 'active' && (
          <>
            <button
              onClick={handleExecute}
              className="flex-1 btn-primary text-sm py-2"
            >
              Execute Now
            </button>
            <button
              onClick={handlePause}
              className="flex-1 btn-outline text-sm py-2"
            >
              Pause
            </button>
          </>
        )}
        {campaign.status === 'paused' && (
          <button
            onClick={async () => {
              await campaignApi.activate(campaign.id);
              onUpdate();
            }}
            className="flex-1 btn-primary text-sm py-2"
          >
            Activate
          </button>
        )}
      </div>
    </div>
  );
}