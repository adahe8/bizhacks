// frontend/components/SpendOptimizationChart.tsx
import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface DataPoint {
  date: Date;
  optimal: number;
  nonOptimal: number;
}

interface Props {
  data: DataPoint[];
}

export default function SpendOptimizationChart({ data }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Check if we have meaningful data
    const hasData = data.length > 0 && data.some(d => d.optimal > 0 || d.nonOptimal > 0);
    
    if (!hasData) {
      // Show empty state
      const width = 600;
      const height = 300;
      
      svg.append('text')
        .attr('x', width / 2)
        .attr('y', height / 2)
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .style('font-size', '16px')
        .style('fill', '#6b7280')
        .text('No optimization data available yet');
      
      svg.append('text')
        .attr('x', width / 2)
        .attr('y', height / 2 + 25)
        .attr('text-anchor', 'middle')
        .style('font-size', '14px')
        .style('fill', '#9ca3af')
        .text('Run campaigns to see performance metrics');
      
      return;
    }

    const width = 600;
    const height = 300;
    const margin = { top: 20, right: 80, bottom: 30, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Scales
    const x = d3.scaleTime()
      .domain(d3.extent(data, d => d.date) as [Date, Date])
      .range([0, innerWidth]);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => Math.max(d.optimal, d.nonOptimal)) || 0])
      .range([innerHeight, 0]);

    // Line generators
    const optimalLine = d3.line<DataPoint>()
      .x(d => x(d.date))
      .y(d => y(d.optimal))
      .curve(d3.curveMonotoneX);

    const nonOptimalLine = d3.line<DataPoint>()
      .x(d => x(d.date))
      .y(d => y(d.nonOptimal))
      .curve(d3.curveMonotoneX);

    // Add X axis
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x).tickFormat((d) => d3.timeFormat('%m/%d')(d as Date)))
      .selectAll('text')
      .style('font-size', '10px');

    // Add Y axis
    g.append('g')
      .call(d3.axisLeft(y).tickFormat(d => `${d3.format('.1s')(d as number)}`))
      .selectAll('text')
      .style('font-size', '10px');

    // Add Y axis label
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left)
      .attr('x', 0 - (innerHeight / 2))
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
      .style('font-size', '12px')
      .text('Total Reach');

    // Add optimal line
    g.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', '#0ea5e9')
      .attr('stroke-width', 2)
      .attr('d', optimalLine);

    // Add non-optimal line
    g.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', '#ef4444')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '5,5')
      .attr('d', nonOptimalLine);

    // Add legend
    const legend = g.append('g')
      .attr('transform', `translate(${innerWidth - 100}, 0)`);

    legend.append('line')
      .attr('x1', 0)
      .attr('x2', 20)
      .attr('y1', 0)
      .attr('y2', 0)
      .attr('stroke', '#0ea5e9')
      .attr('stroke-width', 2);

    legend.append('text')
      .attr('x', 25)
      .attr('y', 4)
      .style('font-size', '12px')
      .text('Optimal');

    legend.append('line')
      .attr('x1', 0)
      .attr('x2', 20)
      .attr('y1', 20)
      .attr('y2', 20)
      .attr('stroke', '#ef4444')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '5,5');

    legend.append('text')
      .attr('x', 25)
      .attr('y', 24)
      .style('font-size', '12px')
      .text('Non-Optimal');

    // Add performance gain
    if (data.length > 0) {
      const lastPoint = data[data.length - 1];
      if (lastPoint.optimal > 0 && lastPoint.nonOptimal > 0) {
        const gain = ((lastPoint.optimal - lastPoint.nonOptimal) / lastPoint.nonOptimal * 100).toFixed(1);
        
        svg.append('text')
          .attr('x', width / 2)
          .attr('y', height - 5)
          .attr('text-anchor', 'middle')
          .style('font-size', '14px')
          .style('font-weight', 'bold')
          .style('fill', '#059669')
          .text(`+${gain}% Performance Gain`);
      }
    }

  }, [data]);

  return (
    <div className="w-full">
      <svg ref={svgRef} width="600" height="300" className="w-full max-w-full"></svg>
    </div>
  );
}