class ChartManager {
 constructor() {
 this.charts = new Map();
 this.init();
 }
 init() {
 const style = document.createElement('style');
 style.textContent = `
 .chart-container {
 background: var(--surface, #ffffff);
 border: 1px solid var(--border, #e2e8f0);
 border-radius: 8px;
 padding: 20px;
 margin-bottom: 20px;
 }
 .chart-header {
 display: flex;
 justify-content: space-between;
 align-items: center;
 margin-bottom: 16px;
 }
 .chart-title {
 font-size: 16px;
 font-weight: 600;
 color: var(--text, #1e293b);
 margin: 0;
 }
 .chart-subtitle {
 font-size: 12px;
 color: var(--text-muted, #64748b);
 margin: 4px 0 0 0;
 }
 .chart-period {
 font-size: 12px;
 color: var(--text-muted, #64748b);
 background: var(--surface-secondary, #f1f5f9);
 padding: 4px 8px;
 border-radius: 4px;
 border: 1px solid var(--border, #e2e8f0);
 }
 .chart-svg {
 width: 100%;
 height: 200px;
 overflow: visible;
 }
 .chart-bar {
 transition: fill 0.3s ease, opacity 0.3s ease;
 }
 .chart-bar:hover {
 opacity: 0.8;
 }
 .chart-line {
 fill: none;
 stroke-width: 2;
 transition: stroke-width 0.3s ease;
 }
 .chart-line:hover {
 stroke-width: 3;
 }
 .chart-point {
 transition: r 0.3s ease;
 }
 .chart-point:hover {
 r: 6;
 }
 .chart-axis {
 stroke: var(--border, #e2e8f0);
 stroke-width: 1;
 }
 .chart-axis-text {
 fill: var(--text-muted, #64748b);
 font-size: 11px;
 font-family: system-ui, sans-serif;
 }
 .chart-grid {
 stroke: var(--border, #e2e8f0);
 stroke-width: 0.5;
 opacity: 0.5;
 }
 .chart-tooltip {
 position: absolute;
 background: var(--surface, #ffffff);
 border: 1px solid var(--border, #e2e8f0);
 border-radius: 6px;
 padding: 8px 12px;
 font-size: 12px;
 box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
 pointer-events: none;
 z-index: 1000;
 opacity: 0;
 transition: opacity 0.2s ease;
 }
 .chart-tooltip.show {
 opacity: 1;
 }
 .chart-legend {
 display: flex;
 gap: 16px;
 margin-top: 12px;
 flex-wrap: wrap;
 }
 .chart-legend-item {
 display: flex;
 align-items: center;
 gap: 6px;
 font-size: 12px;
 color: var(--text-muted, #64748b);
 }
 .chart-legend-color {
 width: 12px;
 height: 12px;
 border-radius: 2px;
 }
 .chart-stats {
 display: grid;
 grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
 gap: 16px;
 margin-top: 16px;
 }
 .chart-stat {
 text-align: center;
 padding: 12px;
 background: var(--surface-secondary, #f1f5f9);
 border-radius: 6px;
 }
 .chart-stat-value {
 font-size: 20px;
 font-weight: 700;
 color: var(--text, #1e293b);
 margin-bottom: 4px;
 }
 .chart-stat-label {
 font-size: 11px;
 color: var(--text-muted, #64748b);
 text-transform: uppercase;
 letter-spacing: 0.05em;
 }
 [data-theme="dark"] .chart-container {
 background: var(--surface, #1e1b4b);
 border-color: var(--border, #3730a3);
 }
 [data-theme="dark"] .chart-period {
 background: var(--surface-secondary, #2d2a5e);
 border-color: var(--border, #3730a3);
 }
 [data-theme="dark"] .chart-stat {
 background: var(--surface-secondary, #2d2a5e);
 }
 [data-theme="dark"] .chart-tooltip {
 background: var(--surface, #1e1b4b);
 border-color: var(--border, #3730a3);
 }
 `;
 document.head.appendChild(style);
 }
 createChart(containerId, options = {}) {
 const {
 type = 'line', 
 title = 'Chart',
 subtitle = '',
 data = [],
 colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
 showLegend = true,
 showGrid = true,
 showTooltip = true,
 period = '',
 height = 200
 } = options;
 const container = document.getElementById(containerId);
 if (!container) return;
 const chartId = `chart-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
 container.innerHTML = `
 <div class="chart-container">
 <div class="chart-header">
 <div>
 <h3 class="chart-title">${title}</h3>
 ${subtitle ? `<p class="chart-subtitle">${subtitle}</p>` : ''}
 </div>
 ${period ? `<div class="chart-period">${period}</div>` : ''}
 </div>
 <div style="position: relative;">
 <svg class="chart-svg" id="${chartId}" style="height: ${height}px;"></svg>
 ${showTooltip ? `<div class="chart-tooltip" id="${chartId}-tooltip"></div>` : ''}
 </div>
 ${showLegend ? `<div class="chart-legend" id="${chartId}-legend"></div>` : ''}
 </div>
 `;
 const chart = {
 id: chartId,
 type,
 data,
 colors,
 showLegend,
 showGrid,
 showTooltip,
 height,
 svg: document.getElementById(chartId),
 tooltip: showTooltip ? document.getElementById(`${chartId}-tooltip`) : null,
 legend: showLegend ? document.getElementById(`${chartId}-legend`) : null
 };
 this.charts.set(chartId, chart);
 this.renderChart(chartId);
 return chartId;
 }
 renderChart(chartId) {
 const chart = this.charts.get(chartId);
 if (!chart) return;
 const { type, data, svg } = chart;
 svg.innerHTML = '';
 if (!data || data.length === 0) {
 this.renderEmptyState(chart);
 return;
 }
 switch (type) {
 case 'line':
 this.renderLineChart(chart);
 break;
 case 'bar':
 this.renderBarChart(chart);
 break;
 case 'pie':
 this.renderPieChart(chart);
 break;
 case 'donut':
 this.renderDonutChart(chart);
 break;
 default:
 this.renderLineChart(chart);
 }
 if (chart.showLegend) {
 this.renderLegend(chart);
 }
 }
 renderLineChart(chart) {
 const { svg, data, colors, showGrid, showTooltip, height } = chart;
 const width = svg.clientWidth || 400;
 const padding = { top: 20, right: 20, bottom: 40, left: 40 };
 const chartWidth = width - padding.left - padding.right;
 const chartHeight = height - padding.top - padding.bottom;
 const maxY = Math.max(...data.map(d => d.value));
 const minY = Math.min(...data.map(d => d.value));
 const yRange = maxY - minY || 1;
 const xStep = chartWidth / (data.length - 1 || 1);
 if (showGrid) {
 const gridLines = 5;
 for (let i = 0; i <= gridLines; i++) {
 const y = padding.top + (chartHeight * i / gridLines);
 svg.innerHTML += `<line class="chart-grid" x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}"/>`;
 }
 }
 svg.innerHTML += `<line class="chart-axis" x1="${padding.left}" y1="${padding.top}" x2="${padding.left}" y2="${height - padding.bottom}"/>`;
 svg.innerHTML += `<line class="chart-axis" x1="${padding.left}" y1="${height - padding.bottom}" x2="${width - padding.right}" y2="${height - padding.bottom}"/>`;
 const yLabels = 5;
 for (let i = 0; i <= yLabels; i++) {
 const value = minY + (yRange * (yLabels - i) / yLabels);
 const y = padding.top + (chartHeight * i / yLabels);
 svg.innerHTML += `<text class="chart-axis-text" x="${padding.left - 8}" y="${y + 4}" text-anchor="end">${Math.round(value)}</text>`;
 }
 let pathData = '';
 const points = [];
 data.forEach((d, i) => {
 const x = padding.left + (i * xStep);
 const y = padding.top + chartHeight - ((d.value - minY) / yRange * chartHeight);
 points.push({ x, y, data: d });
 if (i === 0) {
 pathData += `M ${x} ${y}`;
 } else {
 pathData += ` L ${x} ${y}`;
 }
 });
 svg.innerHTML += `<path class="chart-line" d="${pathData}" stroke="${colors[0]}" fill="none"/>`;
 points.forEach((point, i) => {
 svg.innerHTML += `
 <circle class="chart-point" 
 cx="${point.x}" 
 cy="${point.y}" 
 r="4" 
 fill="${colors[0]}"
 data-index="${i}"
 style="cursor: pointer;"/>
 `;
 });
 data.forEach((d, i) => {
 const x = padding.left + (i * xStep);
 svg.innerHTML += `<text class="chart-axis-text" x="${x}" y="${height - padding.bottom + 16}" text-anchor="middle">${d.label}</text>`;
 });
 if (showTooltip) {
 this.addTooltipEvents(chart, points);
 }
 }
 renderBarChart(chart) {
 const { svg, data, colors, showGrid, showTooltip, height } = chart;
 const width = svg.clientWidth || 400;
 const padding = { top: 20, right: 20, bottom: 40, left: 40 };
 const chartWidth = width - padding.left - padding.right;
 const chartHeight = height - padding.top - padding.bottom;
 const maxY = Math.max(...data.map(d => d.value));
 const barWidth = chartWidth / data.length * 0.8;
 const barSpacing = chartWidth / data.length * 0.2;
 if (showGrid) {
 const gridLines = 5;
 for (let i = 0; i <= gridLines; i++) {
 const y = padding.top + (chartHeight * i / gridLines);
 svg.innerHTML += `<line class="chart-grid" x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}"/>`;
 }
 }
 svg.innerHTML += `<line class="chart-axis" x1="${padding.left}" y1="${padding.top}" x2="${padding.left}" y2="${height - padding.bottom}"/>`;
 svg.innerHTML += `<line class="chart-axis" x1="${padding.left}" y1="${height - padding.bottom}" x2="${width - padding.right}" y2="${height - padding.bottom}"/>`;
 const yLabels = 5;
 for (let i = 0; i <= yLabels; i++) {
 const value = maxY * (yLabels - i) / yLabels;
 const y = padding.top + (chartHeight * i / yLabels);
 svg.innerHTML += `<text class="chart-axis-text" x="${padding.left - 8}" y="${y + 4}" text-anchor="end">${Math.round(value)}</text>`;
 }
 const bars = [];
 data.forEach((d, i) => {
 const x = padding.left + (i * (barWidth + barSpacing)) + barSpacing / 2;
 const barHeight = (d.value / maxY) * chartHeight;
 const y = height - padding.bottom - barHeight;
 bars.push({ x, y, width: barWidth, height: barHeight, data: d });
 svg.innerHTML += `
 <rect class="chart-bar" 
 x="${x}" 
 y="${y}" 
 width="${barWidth}" 
 height="${barHeight}" 
 fill="${colors[i % colors.length]}"
 data-index="${i}"
 style="cursor: pointer;"/>
 `;
 });
 data.forEach((d, i) => {
 const x = padding.left + (i * (barWidth + barSpacing)) + barSpacing / 2 + barWidth / 2;
 svg.innerHTML += `<text class="chart-axis-text" x="${x}" y="${height - padding.bottom + 16}" text-anchor="middle">${d.label}</text>`;
 });
 if (showTooltip) {
 this.addTooltipEvents(chart, bars);
 }
 }
 renderPieChart(chart) {
 const { svg, data, colors, showTooltip, height } = chart;
 const width = svg.clientWidth || 400;
 const radius = Math.min(width, height) / 2 - 20;
 const centerX = width / 2;
 const centerY = height / 2;
 const total = data.reduce((sum, d) => sum + d.value, 0);
 let currentAngle = -Math.PI / 2; 
 const slices = [];
 data.forEach((d, i) => {
 const sliceAngle = (d.value / total) * 2 * Math.PI;
 const startAngle = currentAngle;
 const endAngle = currentAngle + sliceAngle;
 const x1 = centerX + radius * Math.cos(startAngle);
 const y1 = centerY + radius * Math.sin(startAngle);
 const x2 = centerX + radius * Math.cos(endAngle);
 const y2 = centerY + radius * Math.sin(endAngle);
 const largeArc = sliceAngle > Math.PI ? 1 : 0;
 const pathData = `M ${centerX} ${centerY} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`;
 slices.push({ 
 path: pathData, 
 data: d, 
 percentage: (d.value / total * 100).toFixed(1),
 startAngle,
 endAngle
 });
 svg.innerHTML += `
 <path class="chart-slice" 
 d="${pathData}" 
 fill="${colors[i % colors.length]}"
 data-index="${i}"
 style="cursor: pointer;"/>
 `;
 currentAngle = endAngle;
 });
 if (showTooltip) {
 this.addTooltipEvents(chart, slices);
 }
 }
 renderDonutChart(chart) {
 const { svg, data, colors, showTooltip, height } = chart;
 const width = svg.clientWidth || 400;
 const outerRadius = Math.min(width, height) / 2 - 20;
 const innerRadius = outerRadius * 0.6;
 const centerX = width / 2;
 const centerY = height / 2;
 const total = data.reduce((sum, d) => sum + d.value, 0);
 let currentAngle = -Math.PI / 2;
 const slices = [];
 data.forEach((d, i) => {
 const sliceAngle = (d.value / total) * 2 * Math.PI;
 const startAngle = currentAngle;
 const endAngle = currentAngle + sliceAngle;
 const x1 = centerX + outerRadius * Math.cos(startAngle);
 const y1 = centerY + outerRadius * Math.sin(startAngle);
 const x2 = centerX + outerRadius * Math.cos(endAngle);
 const y2 = centerY + outerRadius * Math.sin(endAngle);
 const x3 = centerX + innerRadius * Math.cos(endAngle);
 const y3 = centerY + innerRadius * Math.sin(endAngle);
 const x4 = centerX + innerRadius * Math.cos(startAngle);
 const y4 = centerY + innerRadius * Math.sin(startAngle);
 const largeArc = sliceAngle > Math.PI ? 1 : 0;
 const pathData = `M ${x1} ${y1} A ${outerRadius} ${outerRadius} 0 ${largeArc} 1 ${x2} ${y2} L ${x3} ${y3} A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${x4} ${y4} Z`;
 slices.push({ 
 path: pathData, 
 data: d, 
 percentage: (d.value / total * 100).toFixed(1),
 startAngle,
 endAngle
 });
 svg.innerHTML += `
 <path class="chart-slice" 
 d="${pathData}" 
 fill="${colors[i % colors.length]}"
 data-index="${i}"
 style="cursor: pointer;"/>
 `;
 currentAngle = endAngle;
 });
 svg.innerHTML += `
 <text x="${centerX}" y="${centerY - 8}" text-anchor="middle" class="chart-axis-text" style="font-size: 20px; font-weight: bold;">${total}</text>
 <text x="${centerX}" y="${centerY + 12}" text-anchor="middle" class="chart-axis-text" style="font-size: 12px;">Total</text>
 `;
 if (showTooltip) {
 this.addTooltipEvents(chart, slices);
 }
 }
 renderEmptyState(chart) {
 const { svg, height } = chart;
 const width = svg.clientWidth || 400;
 svg.innerHTML = `
 <text x="${width / 2}" y="${height / 2 - 10}" text-anchor="middle" class="chart-axis-text" style="font-size: 14px;">
 Aucune donnée disponible
 </text>
 <text x="${width / 2}" y="${height / 2 + 10}" text-anchor="middle" class="chart-axis-text" style="font-size: 12px;">
 📊
 </text>
 `;
 }
 renderLegend(chart) {
 const { legend, data, colors } = chart;
 if (!legend) return;
 legend.innerHTML = data.map((d, i) => `
 <div class="chart-legend-item">
 <div class="chart-legend-color" style="background: ${colors[i % colors.length]};"></div>
 <span>${d.label}</span>
 </div>
 `).join('');
 }
 addTooltipEvents(chart, elements) {
 const { svg, tooltip, data } = chart;
 if (!tooltip) return;
 svg.addEventListener('mousemove', (e) => {
 const rect = svg.getBoundingClientRect();
 tooltip.style.left = (e.clientX - rect.left + 10) + 'px';
 tooltip.style.top = (e.clientY - rect.top - 10) + 'px';
 });
 svg.addEventListener('mouseleave', () => {
 tooltip.classList.remove('show');
 });
 svg.querySelectorAll('[data-index]').forEach((element, i) => {
 element.addEventListener('mouseenter', () => {
 const d = data[i];
 const percentage = elements[i]?.percentage;
 tooltip.innerHTML = `
 <div style="font-weight: 600;">${d.label}</div>
 <div>Valeur: ${d.value}</div>
 ${percentage ? `<div>Pourcentage: ${percentage}%</div>` : ''}
 `;
 tooltip.classList.add('show');
 });
 element.addEventListener('mouseleave', () => {
 tooltip.classList.remove('show');
 });
 });
 }
 updateChart(chartId, newData) {
 const chart = this.charts.get(chartId);
 if (!chart) return;
 chart.data = newData;
 this.renderChart(chartId);
 }
 destroyChart(chartId) {
 this.charts.delete(chartId);
 }
 createStatsCards(containerId, stats = []) {
 const container = document.getElementById(containerId);
 if (!container) return;
 container.innerHTML = `
 <div class="chart-stats">
 ${stats.map(stat => `
 <div class="chart-stat">
 <div class="chart-stat-value">${stat.value}</div>
 <div class="chart-stat-label">${stat.label}</div>
 </div>
 `).join('')}
 </div>
 `;
 }
}
const charts = new ChartManager();
if (typeof module !== 'undefined' && module.exports) {
 module.exports = { ChartManager, charts };
}