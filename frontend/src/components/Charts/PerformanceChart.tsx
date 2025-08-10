import React, { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import * as d3 from 'd3'

interface PerformanceData {
  date: string
  roe: number
  roa: number
  nim: number
  efficiency: number
}

const mockData: PerformanceData[] = [
  { date: '2020-01', roe: 12.5, roa: 1.2, nim: 2.8, efficiency: 65.2 },
  { date: '2020-04', roe: 11.8, roa: 1.1, nim: 2.7, efficiency: 66.1 },
  { date: '2020-07', roe: 10.2, roa: 0.9, nim: 2.5, efficiency: 68.3 },
  { date: '2020-10', roe: 9.8, roa: 0.8, nim: 2.3, efficiency: 70.1 },
  { date: '2021-01', roe: 11.2, roa: 1.0, nim: 2.6, efficiency: 67.5 },
  { date: '2021-04', roe: 12.8, roa: 1.3, nim: 2.9, efficiency: 64.8 },
  { date: '2021-07', roe: 13.5, roa: 1.4, nim: 3.1, efficiency: 63.2 },
  { date: '2021-10', roe: 14.2, roa: 1.5, nim: 3.2, efficiency: 62.1 },
  { date: '2022-01', roe: 13.8, roa: 1.4, nim: 3.0, efficiency: 63.8 },
  { date: '2022-04', roe: 12.9, roa: 1.2, nim: 2.8, efficiency: 65.4 },
  { date: '2022-07', roe: 11.5, roa: 1.0, nim: 2.5, efficiency: 67.9 },
  { date: '2022-10', roe: 10.8, roa: 0.9, nim: 2.3, efficiency: 69.2 },
  { date: '2023-01', roe: 11.9, roa: 1.1, nim: 2.6, efficiency: 66.8 },
  { date: '2023-04', roe: 12.6, roa: 1.3, nim: 2.9, efficiency: 65.1 },
  { date: '2023-07', roe: 13.2, roa: 1.4, nim: 3.0, efficiency: 64.3 },
  { date: '2023-10', roe: 13.8, roa: 1.5, nim: 3.1, efficiency: 63.5 }
]

export default function PerformanceChart() {
  const svgRef = useRef<SVGSVGElement>(null)
  const [selectedMetric, setSelectedMetric] = useState<'roe' | 'roa' | 'nim' | 'efficiency'>('roe')
  const [hoveredPoint, setHoveredPoint] = useState<PerformanceData | null>(null)

  useEffect(() => {
    if (!svgRef.current) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const margin = { top: 20, right: 30, bottom: 40, left: 60 }
    const width = 400 - margin.left - margin.right
    const height = 300 - margin.top - margin.bottom

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    // Scales
    const x = d3.scaleTime()
      .domain(d3.extent(mockData, d => new Date(d.date)) as [Date, Date])
      .range([0, width])

    const y = d3.scaleLinear()
      .domain([0, d3.max(mockData, d => d[selectedMetric]) as number * 1.1])
      .range([height, 0])

    // Line generator
    const line = d3.line<PerformanceData>()
      .x(d => x(new Date(d.date)))
      .y(d => y(d[selectedMetric]))
      .curve(d3.curveMonotoneX)

    // Add gradient
    const gradient = g.append('defs')
      .append('linearGradient')
      .attr('id', 'line-gradient')
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('x1', 0)
      .attr('y1', y(0))
      .attr('x2', 0)
      .attr('y2', y(d3.max(mockData, d => d[selectedMetric]) as number))

    gradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#3b82f6')
      .attr('stop-opacity', 0.8)

    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#3b82f6')
      .attr('stop-opacity', 0.1)

    // Add area
    const area = d3.area<PerformanceData>()
      .x(d => x(new Date(d.date)))
      .y0(y(0))
      .y1(d => y(d[selectedMetric]))
      .curve(d3.curveMonotoneX)

    g.append('path')
      .datum(mockData)
      .attr('fill', 'url(#line-gradient)')
      .attr('d', area)

    // Add line
    g.append('path')
      .datum(mockData)
      .attr('fill', 'none')
      .attr('stroke', '#3b82f6')
      .attr('stroke-width', 3)
      .attr('d', line)

    // Add dots
    g.selectAll('.dot')
      .data(mockData)
      .enter()
      .append('circle')
      .attr('class', 'dot')
      .attr('cx', d => x(new Date(d.date)))
      .attr('cy', d => y(d[selectedMetric]))
      .attr('r', 4)
      .attr('fill', '#3b82f6')
      .attr('stroke', 'white')
      .attr('stroke-width', 2)
      .on('mouseover', (event, d) => {
        setHoveredPoint(d)
        d3.select(event.currentTarget).attr('r', 6).attr('fill', '#1d4ed8')
      })
      .on('mouseout', (event) => {
        setHoveredPoint(null)
        d3.select(event.currentTarget).attr('r', 4).attr('fill', '#3b82f6')
      })

    // Add axes
    const xAxis = d3.axisBottom(x).tickFormat(d3.timeFormat('%b %Y'))
    const yAxis = d3.axisLeft(y).ticks(5)

    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(xAxis)
      .selectAll('text')
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '.15em')
      .attr('transform', 'rotate(-45)')

    g.append('g')
      .call(yAxis)

    // Add grid
    g.append('g')
      .attr('class', 'grid')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x).tickSize(-height).tickFormat(() => ''))

    g.append('g')
      .attr('class', 'grid')
      .call(d3.axisLeft(y).tickSize(-width).tickFormat(() => ''))

    // Style grid
    svg.selectAll('.grid line')
      .attr('stroke', '#e5e7eb')
      .attr('stroke-opacity', 0.3)

    svg.selectAll('.grid path')
      .attr('stroke-width', 0)

  }, [selectedMetric])

  const metrics = [
    { key: 'roe', label: 'ROE (%)', color: 'text-primary-600' },
    { key: 'roa', label: 'ROA (%)', color: 'text-success-600' },
    { key: 'nim', label: 'NIM (%)', color: 'text-warning-600' },
    { key: 'efficiency', label: 'Efficiency (%)', color: 'text-danger-600' }
  ]

  return (
    <div className="space-y-4">
      {/* Metric Selector */}
      <div className="flex flex-wrap gap-2">
        {metrics.map((metric) => (
          <button
            key={metric.key}
            onClick={() => setSelectedMetric(metric.key as any)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              selectedMetric === metric.key
                ? 'bg-primary-100 text-primary-700'
                : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
            }`}
          >
            {metric.label}
          </button>
        ))}
      </div>

      {/* Chart */}
      <div className="relative">
        <svg
          ref={svgRef}
          width="400"
          height="300"
          className="w-full h-auto"
        />
        
        {/* Tooltip */}
        {hoveredPoint && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="absolute bg-white border border-neutral-200 rounded-lg shadow-lg p-3 text-sm"
            style={{
              left: `${(new Date(hoveredPoint.date).getTime() - new Date(mockData[0].date).getTime()) / (new Date(mockData[mockData.length - 1].date).getTime() - new Date(mockData[0].date).getTime()) * 100}%`,
              top: '20px'
            }}
          >
            <div className="font-medium">{hoveredPoint.date}</div>
            <div className="text-neutral-600">
              {selectedMetric.toUpperCase()}: {hoveredPoint[selectedMetric].toFixed(1)}%
            </div>
          </motion.div>
        )}
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-4 text-xs text-neutral-500">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-primary-600 rounded-full"></div>
          <span>Performance Trend</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-primary-200 rounded-full"></div>
          <span>Area Fill</span>
        </div>
      </div>
    </div>
  )
}