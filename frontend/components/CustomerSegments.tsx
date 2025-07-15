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

  if (segments.length === 0) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <p className="text-gray-500">No customer segments defined yet.</p>
          <p className="text-sm text-gray-400 mt-2">
            AI will generate segments based on your market data.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="space-y-4">
        {segments.map((segment, index) => (
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
            {segment.criteria && (
              <div className="mt-2">
                <p className="text-xs text-gray-500">
                  Criteria: {JSON.parse(segment.criteria).age_range || 'Various demographics'}
                </p>
              </div>
            )}
          </div>
        ))}
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