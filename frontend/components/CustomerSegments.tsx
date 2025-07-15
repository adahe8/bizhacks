import { CustomerSegment } from '@/lib/types';

interface Props {
  segments: CustomerSegment[];
}

export default function CustomerSegments({ segments }: Props) {
  const getSegmentColor = (index: number) => {
    const colors = [
      'bg-blue-100 text-blue-800',
      'bg-green-100 text-green-800',
      'bg-purple-100 text-purple-800',
    ];
    return colors[index % colors.length];
  };

  const renderChannelBar = (distribution: any) => {
    if (!distribution) return null;
    
    const channels = [
      { name: 'Email', key: 'email', color: 'bg-blue-500' },
      { name: 'Facebook', key: 'facebook', color: 'bg-indigo-500' },
      { name: 'Google', key: 'google_seo', color: 'bg-green-500' }
    ];
    
    return (
      <div className="mt-3">
        <p className="text-xs text-gray-500 mb-1">Channel Distribution</p>
        <div className="flex h-6 rounded overflow-hidden">
          {channels.map((channel) => {
            const percentage = distribution[channel.key] || 0;
            if (percentage === 0) return null;
            
            return (
              <div
                key={channel.key}
                className={`${channel.color} flex items-center justify-center text-white text-xs font-medium`}
                style={{ width: `${percentage}%` }}
                title={`${channel.name}: ${percentage}%`}
              >
                {percentage > 15 && `${percentage}%`}
              </div>
            );
          })}
        </div>
        <div className="flex justify-between mt-1">
          {channels.map((channel) => (
            <span key={channel.key} className="text-xs text-gray-500">
              {channel.name}: {distribution[channel.key] || 0}%
            </span>
          ))}
        </div>
      </div>
    );
  };

  const renderPurchaseInfo = (criteria: any) => {
    if (!criteria) return null;
    
    const avgPurchases = criteria.avg_purchases || 0;
    const purchaseRange = criteria.purchase_range || 'N/A';
    const highPurchasersPct = criteria.high_purchasers_pct || 0;
    const noPurchasePct = criteria.no_purchase_pct || 0;
    
    return (
      <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
        <p className="font-medium text-gray-700">Purchase Patterns:</p>
        <div className="grid grid-cols-2 gap-2 mt-1">
          <div>
            <span className="text-gray-500">Avg Purchases:</span>
            <span className="ml-1 font-medium">{avgPurchases.toFixed(1)}</span>
          </div>
          <div>
            <span className="text-gray-500">Range:</span>
            <span className="ml-1 font-medium">{purchaseRange}</span>
          </div>
          <div>
            <span className="text-gray-500">Frequent Buyers:</span>
            <span className="ml-1 font-medium text-green-600">{highPurchasersPct}%</span>
          </div>
          <div>
            <span className="text-gray-500">No Purchases:</span>
            <span className="ml-1 font-medium text-red-600">{noPurchasePct}%</span>
          </div>
        </div>
      </div>
    );
  };

  if (segments.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center py-8">
          <p className="text-gray-500">No customer segments defined yet.</p>
          <p className="text-sm text-gray-400 mt-2">
            AI will generate up to 3 segments based on your user data.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="space-y-4">
        {segments.slice(0, 3).map((segment, index) => {
          const channelDist = segment.channel_distribution ? 
            (typeof segment.channel_distribution === 'string' ? 
              JSON.parse(segment.channel_distribution) : 
              segment.channel_distribution) : null;
          
          const criteria = segment.criteria ? 
            (typeof segment.criteria === 'string' ? 
              JSON.parse(segment.criteria) : 
              segment.criteria) : null;
          
          return (
            <div
              key={segment.id}
              className="border-l-4 border-primary-500 pl-4 py-2"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{segment.name}</h4>
                  <p className="text-sm text-gray-600 mt-1">
                    {segment.description}
                  </p>
                </div>
                <div className="ml-4">
                  <span className={`px-3 py-1 text-sm font-medium rounded-full ${getSegmentColor(index)}`}>
                    {segment.size}%
                  </span>
                </div>
              </div>
              
              {criteria && (
                <>
                  <div className="mt-2 text-xs text-gray-500">
                    <p>Age: {criteria.age_range || criteria.avg_age || 'Various'}</p>
                    {criteria.top_locations && (
                      <p>Locations: {criteria.top_locations.slice(0, 2).join(', ')}</p>
                    )}
                  </div>
                  {renderPurchaseInfo(criteria)}
                </>
              )}
              
              {channelDist && renderChannelBar(channelDist)}
            </div>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t">
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500">
            Total Segments: {Math.min(segments.length, 3)}
          </p>
          <p className="text-sm text-gray-500">
            Coverage: {segments.slice(0, 3).reduce((sum, seg) => sum + (seg.size || 0), 0).toFixed(1)}%
          </p>
        </div>
      </div>
    </div>
  );
}