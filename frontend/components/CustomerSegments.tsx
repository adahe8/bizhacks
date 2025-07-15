// components/CustomerSegments.tsx
import { useState } from 'react';
import { FaUsers, FaChartPie, FaArrowRight, FaTag } from 'react-icons/fa';

interface Segment {
  id: number;
  name: string;
  description: string;
  size_estimate: number;
}

interface CustomerSegmentsProps {
  segments: Segment[];
}

export default function CustomerSegments({ segments }: CustomerSegmentsProps) {
  const [selectedSegment, setSelectedSegment] = useState<number | null>(null);
  
  const totalCustomers = segments.reduce((sum, seg) => sum + seg.size_estimate, 0);
  
  const getSegmentColor = (index: number) => {
    const colors = [
      'bg-blue-500',
      'bg-green-500',
      'bg-purple-500',
      'bg-yellow-500',
      'bg-pink-500',
      'bg-indigo-500'
    ];
    return colors[index % colors.length];
  };
  
  const getSegmentPercentage = (size: number) => {
    return totalCustomers > 0 ? ((size / totalCustomers) * 100).toFixed(1) : '0';
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Segments List */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <FaTag className="mr-2 text-indigo-600" />
              Customer Segments
            </h3>
            <div className="space-y-3">
              {segments.map((segment, index) => (
                <div
                  key={segment.id}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedSegment === segment.id
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedSegment(segment.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className={`w-4 h-4 rounded-full ${getSegmentColor(index)} mr-3`} />
                      <div>
                        <h4 className="font-medium text-gray-900">{segment.name}</h4>
                        <p className="text-sm text-gray-600 mt-1">{segment.description}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-semibold text-gray-900">
                        {segment.size_estimate.toLocaleString()}
                      </p>
                      <p className="text-sm text-gray-600">
                        {getSegmentPercentage(segment.size_estimate)}%
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {segments.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <FaUsers className="mx-auto mb-3 text-4xl text-gray-300" />
                <p>No segments created yet</p>
                <p className="text-sm mt-1">Run customer segmentation to get started</p>
              </div>
            )}
          </div>
          
          {/* Visual Representation */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <FaChartPie className="mr-2 text-indigo-600" />
              Distribution Overview
            </h3>
            
            {segments.length > 0 ? (
              <div className="space-y-4">
                {/* Pie Chart Placeholder */}
                <div className="relative h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <div className="relative w-48 h-48 mx-auto">
                      {/* Simple CSS Pie Chart */}
                      <svg viewBox="0 0 32 32" className="w-full h-full transform -rotate-90">
                        {(() => {
                          let cumulativePercentage = 0;
                          return segments.map((segment, index) => {
                            const percentage = (segment.size_estimate / totalCustomers) * 100;
                            const strokeDasharray = `${percentage} ${100 - percentage}`;
                            const strokeDashoffset = -cumulativePercentage;
                            
                            cumulativePercentage += percentage;
                            
                            // Map color class to hex color
                            const colorMap: { [key: string]: string } = {
                              'bg-blue-500': '#3B82F6',
                              'bg-green-500': '#10B981',
                              'bg-purple-500': '#8B5CF6',
                              'bg-yellow-500': '#F59E0B',
                              'bg-pink-500': '#EC4899',
                              'bg-indigo-500': '#6366F1'
                            };
                            
                            const color = colorMap[getSegmentColor(index)] || '#6366F1';
                            
                            return (
                              <circle
                                key={segment.id}
                                r="16"
                                cx="16"
                                cy="16"
                                fill="none"
                                stroke={color}
                                strokeWidth="32"
                                strokeDasharray={strokeDasharray}
                                strokeDashoffset={strokeDashoffset}
                                className="transition-all duration-300"
                              />
                            );
                          });
                        })()}
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div>
                          <p className="text-3xl font-bold text-gray-900">
                            {totalCustomers.toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-600">Total Customers</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Actions */}
                <div className="flex justify-center">
                  <button
                    onClick={() => window.location.href = '/create'}
                    disabled={segments.length === 0}
                    className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Create Campaigns for Segments
                    <FaArrowRight className="ml-2" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                <p className="text-gray-500">No data to display</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}