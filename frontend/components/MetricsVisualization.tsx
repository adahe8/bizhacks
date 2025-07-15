// components/MetricsVisualization.tsx
import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { FaChartLine, FaMousePointer, FaExchangeAlt, FaDollarSign } from 'react-icons/fa';

interface Metrics {
  channel: string;
  impressions: number;
  clicks: number;
  conversions: number;
  spend: number;
  roi: number;
}

interface MetricsVisualizationProps {
  metrics: Metrics;
  detailed?: boolean;
}

export default function MetricsVisualization({ metrics, detailed = false }: MetricsVisualizationProps) {
  const chartRef = useRef<SVGSVGElement>(null);
  const ctr = metrics.impressions > 0 ? (metrics.clicks / metrics.impressions) * 100 : 0;
  const conversionRate = metrics.clicks > 0 ? (metrics.conversions / metrics.clicks) * 100 : 0;

  useEffect(() => {
    if (detailed && chartRef.current) {
      drawDetailedChart();
    }
  }, [metrics, detailed]);

  const drawDetailedChart = () => {
    if (!chartRef.current) return;

    // Clear previous chart
    d3.select(chartRef.current).selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const width = 400 - margin.left - margin.right;
    const height = 200 - margin.top - margin.bottom;

    const svg = d3.select(chartRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Data for the funnel
    const data = [
      { stage: 'Impressions', value: metrics.impressions },
      { stage: 'Clicks', value: metrics.clicks },
      { stage: 'Conversions', value: metrics.conversions }
    ];

    const x = d3.scaleBand()
      .range([0, width])
      .domain(data.map(d => d.stage))
      .padding(0.1);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value) || 0])
      .range([height, 0]);

    // Add bars
    g.selectAll('.bar')
      .data(data)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(d.stage) || 0)
      .attr('width', x.bandwidth())
      .attr('y', height)
      .attr('height', 0)
      .attr('fill', (d, i) => ['#6366f1', '#10b981', '#f59e0b'][i])
      .transition()
      .duration(750)
      .attr('y', d => y(d.value))
      .attr('height', d => height - y(d.value));

    // Add value labels
    g.selectAll('.label')
      .data(data)
      .enter().append('text')
      .attr('class', 'label')
      .attr('x', d => (x(d.stage) || 0) + x.bandwidth() / 2)
      .attr('y', d => y(d.value) - 5)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('fill', '#4b5563')
      .text(d => d.value.toLocaleString());

    // Add x axis
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .attr('font-size', '12px');

    // Add y axis
    g.append('g')
      .call(d3.axisLeft(y).ticks(5).tickFormat(d => {
        if (typeof d === 'number') {
          return d >= 1000 ? `${(d / 1000).toFixed(0)}k` : d.toString();
        }
        return '';
      }))
      .selectAll('text')
      .attr('font-size', '12px');
  };

  if (detailed) {
    return (
      <div>
        <svg ref={chartRef}></svg>
        <div className="mt-4 grid grid-cols-2 gap-4">
          <MetricCard
            icon={<FaMousePointer />}
            label="CTR"
            value={`${ctr.toFixed(2)}%`}
            color="text-blue-600"
          />
          <MetricCard
            icon={<FaExchangeAlt />}
            label="Conv. Rate"
            value={`${conversionRate.toFixed(2)}%`}
            color="text-green-600"
          />
          <MetricCard
            icon={<FaDollarSign />}
            label="Spend"
            value={`$${metrics.spend.toLocaleString()}`}
            color="text-purple-600"
          />
          <MetricCard
            icon={<FaChartLine />}
            label="ROI"
            value={`${metrics.roi.toFixed(1)}x`}
            color="text-amber-600"
          />
        </div>
      </div>
    );
  }

  // Simple metrics display
  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-600">Impressions</span>
        <span className="text-sm font-semibold">{metrics.impressions.toLocaleString()}</span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-600">Clicks</span>
        <span className="text-sm font-semibold">{metrics.clicks.toLocaleString()}</span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-600">CTR</span>
        <span className="text-sm font-semibold">{ctr.toFixed(2)}%</span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-600">ROI</span>
        <span className="text-sm font-semibold text-green-600">{metrics.roi.toFixed(1)}x</span>
      </div>
    </div>
  );
}

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  color: string;
}

function MetricCard({ icon, label, value, color }: MetricCardProps) {
  return (
    <div className="bg-gray-50 rounded-lg p-3">
      <div className={`flex items-center ${color} mb-1`}>
        {icon}
        <span className="ml-2 text-xs font-medium">{label}</span>
      </div>
      <p className="text-lg font-bold text-gray-900">{value}</p>
    </div>
  );
}