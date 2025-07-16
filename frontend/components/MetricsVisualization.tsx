import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { ChannelMetrics } from '@/lib/types';

interface Props {
  metrics: ChannelMetrics;
}

export default function MetricsVisualization({ metrics }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !metrics) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 300;
    const height = 200;
    const margin = { top: 20, right: 20, bottom: 30, left: 50 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Data for visualization
    const data = [
      { metric: 'CTR', value: metrics.avg_engagement_rate * 100 },
      { metric: 'Conv', value: metrics.avg_conversion_rate * 100 },
    ];

    // Scales
    const x = d3.scaleBand()
      .range([0, innerWidth])
      .padding(0.3)
      .domain(data.map(d => d.metric));

    const y = d3.scaleLinear()
      .range([innerHeight, 0])
      .domain([0, Math.max(...data.map(d => d.value)) * 1.2]);

    // Bars
    g.selectAll('.bar')
      .data(data)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(d.metric) || 0)
      .attr('width', x.bandwidth())
      .attr('y', innerHeight)
      .attr('height', 0)
      .attr('fill', '#0ea5e9')
      .transition()
      .duration(800)
      .attr('y', d => y(d.value))
      .attr('height', d => innerHeight - y(d.value));

    // X axis
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .style('font-size', '12px');

    // Y axis
    g.append('g')
      .call(d3.axisLeft(y).ticks(5).tickFormat(d => `${d}%`))
      .selectAll('text')
      .style('font-size', '12px');

    // Value labels
    g.selectAll('.label')
      .data(data)
      .enter().append('text')
      .attr('class', 'label')
      .attr('x', d => (x(d.metric) || 0) + x.bandwidth() / 2)
      .attr('y', d => y(d.value) - 5)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('font-weight', 'bold')
      .text(d => `${d.value.toFixed(1)}%`);

  }, [metrics]);

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

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <div className="metric-card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <span className="text-2xl mr-2">{getChannelIcon(metrics.channel)}</span>
          <h3 className="font-semibold text-gray-900 capitalize">{metrics.channel}</h3>
        </div>
        <span className="text-sm text-gray-500">{metrics.total_campaigns} campaigns</span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-500">Impressions</p>
          <p className="text-xl font-bold text-gray-900">{formatNumber(metrics.total_impressions)}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Clicks</p>
          <p className="text-xl font-bold text-gray-900">{formatNumber(metrics.total_clicks)}</p>
        </div>
      </div>

      <svg ref={svgRef} width="300" height="200" className="w-full"></svg>

      <div className="mt-4 pt-4 border-t">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Total Spend</span>
          <span className="font-medium">${metrics.total_spend.toFixed(0)}</span>
        </div>
      </div>
    </div>
  );
}