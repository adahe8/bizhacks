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
      'bg-pink-100 text-pink-800',
      'bg-yellow-100 text-yellow-800',
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

  if (segments.length === 0) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <p className="text-gray-500">No customer segments defined yet.</p>
          <p className="text-sm text-gray-400 mt-2">
            AI will generate segments based on your user data.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="space-y-4">
        {segments.map((segment, index) => {
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
                <div className="mt-2 text-xs text-gray-500">
                  <p>Age: {criteria.age_range || criteria.avg_age || 'Various'}</p>
                  {criteria.top_locations && (
                    <p>Locations: {criteria.top_locations.slice(0, 2).join(', ')}</p>
                  )}
                </div>
              )}
              
              {channelDist && renderChannelBar(channelDist)}
            </div>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t">
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500">
            Total Segments: {segments.length}
          </p>
          <p className="text-sm text-gray-500">
            Coverage: {segments.reduce((sum, seg) => sum + (seg.size || 0), 0)}%
          </p>
        </div>
      </div>
    </div>
  );
}