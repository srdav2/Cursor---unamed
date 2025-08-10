// Dashboard JavaScript
class BankDashboard {
    constructor() {
        this.currentBank = null;
        this.currentYear = null;
        this.charts = {};
        this.data = {};
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.initializeCharts();
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Bank and year selectors
        document.getElementById('bankSelect').addEventListener('change', (e) => {
            this.currentBank = e.target.value;
            this.loadBankData();
        });

        document.getElementById('yearSelect').addEventListener('change', (e) => {
            this.currentYear = e.target.value;
            this.loadBankData();
        });

        // Peer comparison
        document.getElementById('peerSelect').addEventListener('change', (e) => {
            this.updatePeerComparison();
        });
    }

    switchTab(tabName) {
        // Remove active class from all tabs and content
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        // Add active class to selected tab and content
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(tabName).classList.add('active');

        // Initialize charts for the new tab
        this.initializeTabCharts(tabName);
    }

    async loadInitialData() {
        // Load sample data for demonstration
        this.data = {
            overview: {
                netInterestIncome: { value: 24800, change: 12.5, trend: [22000, 23500, 24800] },
                netProfitAfterTax: { value: 9200, change: 8.3, trend: [8500, 8900, 9200] },
                returnOnEquity: { value: 14.2, change: 2.1, trend: [12.1, 13.8, 14.2] },
                cet1Ratio: { value: 12.8, change: 0.3, trend: [12.5, 12.7, 12.8] }
            },
            profitability: {
                netInterestMargin: { value: 2.15, change: 0.08, trend: [2.07, 2.12, 2.15] },
                costToIncomeRatio: { value: 45.2, change: -1.2, trend: [46.4, 45.8, 45.2] },
                operatingLeverage: { value: 1.15, change: 0.05, trend: [1.10, 1.12, 1.15] }
            },
            risk: {
                cet1Ratio: { value: 12.8, regulatory: 10.5 },
                liquidityCoverageRatio: { value: 125, regulatory: 100 },
                nonPerformingLoans: { value: 0.85, change: 0.12, trend: [0.73, 0.78, 0.85] }
            },
            liquidity: {
                loanToDepositRatio: { value: 85.2, change: -2.1, trend: [87.3, 86.1, 85.2] },
                wholesaleFunding: { value: 15.8, change: 1.2, trend: [14.6, 15.2, 15.8] },
                liquidAssets: { value: 45200, change: 8.5, trend: [41600, 43200, 45200] }
            },
            efficiency: {
                costToIncomeRatio: { value: 45.2, change: -1.2, trend: [46.4, 45.8, 45.2] },
                revenuePerEmployee: { value: 485, change: 5.8, trend: [458, 472, 485] },
                digitalAdoption: { value: 78.5, change: 12.3, trend: [66.2, 72.1, 78.5] }
            }
        };

        this.updateDashboard();
    }

    async loadBankData() {
        if (!this.currentBank || !this.currentYear) return;

        try {
            // Show loading state
            this.showLoading();

            // Fetch data from backend
            const response = await fetch(`/api/extract?bank=${this.currentBank}&year=${this.currentYear}`);
            const data = await response.json();

            if (data.items) {
                this.processBankData(data.items);
                this.updateDashboard();
            }

        } catch (error) {
            console.error('Error loading bank data:', error);
            this.showError('Failed to load bank data');
        } finally {
            this.hideLoading();
        }
    }

    processBankData(items) {
        // Process the extracted financial data
        const processedData = {};
        
        items.forEach(item => {
            const metricName = item.standard_name;
            const value = parseFloat(item.value) || 0;
            
            processedData[metricName] = {
                value: value,
                unit: item.unit || '',
                confidence: item.confidence || 0,
                source: item.source || ''
            };
        });

        this.data = this.mergeWithSampleData(processedData);
    }

    mergeWithSampleData(extractedData) {
        // Merge extracted data with sample data for demonstration
        const merged = { ...this.data };
        
        // Update overview metrics
        if (extractedData.net_interest_income) {
            merged.overview.netInterestIncome.value = extractedData.net_interest_income.value;
        }
        if (extractedData.net_profit_after_tax) {
            merged.overview.netProfitAfterTax.value = extractedData.net_profit_after_tax.value;
        }
        if (extractedData.roe) {
            merged.overview.returnOnEquity.value = extractedData.roe.value;
        }
        if (extractedData.cet1_ratio) {
            merged.overview.cet1Ratio.value = extractedData.cet1_ratio.value;
        }

        return merged;
    }

    initializeCharts() {
        this.initializeOverviewCharts();
        this.initializeProfitabilityCharts();
        this.initializeRiskCharts();
        this.initializeLiquidityCharts();
        this.initializeEfficiencyCharts();
        this.initializeComparisonCharts();
        this.initializeTrendsCharts();
    }

    initializeTabCharts(tabName) {
        switch(tabName) {
            case 'overview':
                this.initializeOverviewCharts();
                break;
            case 'profitability':
                this.initializeProfitabilityCharts();
                break;
            case 'risk':
                this.initializeRiskCharts();
                break;
            case 'liquidity':
                this.initializeLiquidityCharts();
                break;
            case 'efficiency':
                this.initializeEfficiencyCharts();
                break;
            case 'comparison':
                this.initializeComparisonCharts();
                break;
            case 'trends':
                this.initializeTrendsCharts();
                break;
        }
    }

    initializeOverviewCharts() {
        // Performance Overview Chart
        const performanceCtx = document.getElementById('performanceChart');
        if (performanceCtx && !this.charts.performance) {
            this.charts.performance = new Chart(performanceCtx, {
                type: 'line',
                data: {
                    labels: ['2022', '2023', '2024'],
                    datasets: [{
                        label: 'Net Interest Income',
                        data: [22000, 23500, 24800],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Net Profit After Tax',
                        data: [8500, 8900, 9200],
                        borderColor: '#764ba2',
                        backgroundColor: 'rgba(118, 75, 162, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + (value / 1000) + 'B';
                                }
                            }
                        }
                    }
                }
            });
        }

        // Asset Composition Chart
        const assetCtx = document.getElementById('assetCompositionChart');
        if (assetCtx && !this.charts.assetComposition) {
            this.charts.assetComposition = new Chart(assetCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Loans & Advances', 'Investment Securities', 'Cash & Equivalents', 'Other Assets'],
                    datasets: [{
                        data: [65, 20, 10, 5],
                        backgroundColor: [
                            '#667eea',
                            '#764ba2',
                            '#f093fb',
                            '#f5576c'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }

    initializeProfitabilityCharts() {
        // Revenue Breakdown Chart
        const revenueCtx = document.getElementById('revenueBreakdownChart');
        if (revenueCtx && !this.charts.revenueBreakdown) {
            this.charts.revenueBreakdown = new Chart(revenueCtx, {
                type: 'bar',
                data: {
                    labels: ['Net Interest Income', 'Fee Income', 'Trading Income', 'Other Income'],
                    datasets: [{
                        label: 'Revenue (AUD millions)',
                        data: [24800, 8200, 3100, 1800],
                        backgroundColor: [
                            'rgba(102, 126, 234, 0.8)',
                            'rgba(118, 75, 162, 0.8)',
                            'rgba(240, 147, 251, 0.8)',
                            'rgba(245, 87, 108, 0.8)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + (value / 1000) + 'B';
                                }
                            }
                        }
                    }
                }
            });
        }

        // Margin Trends Chart
        const marginCtx = document.getElementById('marginTrendsChart');
        if (marginCtx && !this.charts.marginTrends) {
            this.charts.marginTrends = new Chart(marginCtx, {
                type: 'line',
                data: {
                    labels: ['2022', '2023', '2024'],
                    datasets: [{
                        label: 'Net Interest Margin',
                        data: [2.07, 2.12, 2.15],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            min: 1.8,
                            max: 2.3
                        }
                    }
                }
            });
        }
    }

    initializeRiskCharts() {
        // Capital Structure Chart
        const capitalCtx = document.getElementById('capitalStructureChart');
        if (capitalCtx && !this.charts.capitalStructure) {
            this.charts.capitalStructure = new Chart(capitalCtx, {
                type: 'bar',
                data: {
                    labels: ['CET1', 'AT1', 'Tier 2', 'Total Capital'],
                    datasets: [{
                        label: 'Capital Ratios (%)',
                        data: [12.8, 1.2, 2.0, 16.0],
                        backgroundColor: [
                            'rgba(102, 126, 234, 0.8)',
                            'rgba(118, 75, 162, 0.8)',
                            'rgba(240, 147, 251, 0.8)',
                            'rgba(245, 87, 108, 0.8)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 20
                        }
                    }
                }
            });
        }

        // Risk Metrics Chart
        const riskCtx = document.getElementById('riskMetricsChart');
        if (riskCtx && !this.charts.riskMetrics) {
            this.charts.riskMetrics = new Chart(riskCtx, {
                type: 'radar',
                data: {
                    labels: ['Credit Risk', 'Market Risk', 'Operational Risk', 'Liquidity Risk', 'Interest Rate Risk'],
                    datasets: [{
                        label: 'Risk Level',
                        data: [0.85, 0.45, 0.65, 0.25, 0.55],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.2)',
                        pointBackgroundColor: '#667eea'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 1
                        }
                    }
                }
            });
        }
    }

    initializeLiquidityCharts() {
        // Funding Sources Chart
        const fundingCtx = document.getElementById('fundingSourcesChart');
        if (fundingCtx && !this.charts.fundingSources) {
            this.charts.fundingSources = new Chart(fundingCtx, {
                type: 'pie',
                data: {
                    labels: ['Customer Deposits', 'Wholesale Funding', 'Equity', 'Other'],
                    datasets: [{
                        data: [75, 15, 8, 2],
                        backgroundColor: [
                            '#667eea',
                            '#764ba2',
                            '#f093fb',
                            '#f5576c'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }

        // Liquidity Coverage Chart
        const liquidityCtx = document.getElementById('liquidityCoverageChart');
        if (liquidityCtx && !this.charts.liquidityCoverage) {
            this.charts.liquidityCoverage = new Chart(liquidityCtx, {
                type: 'bar',
                data: {
                    labels: ['LCR', 'NSFR', 'Liquid Assets'],
                    datasets: [{
                        label: 'Ratio (%)',
                        data: [125, 110, 85],
                        backgroundColor: [
                            'rgba(102, 126, 234, 0.8)',
                            'rgba(118, 75, 162, 0.8)',
                            'rgba(240, 147, 251, 0.8)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 150
                        }
                    }
                }
            });
        }
    }

    initializeEfficiencyCharts() {
        // Efficiency Trends Chart
        const efficiencyCtx = document.getElementById('efficiencyTrendsChart');
        if (efficiencyCtx && !this.charts.efficiencyTrends) {
            this.charts.efficiencyTrends = new Chart(efficiencyCtx, {
                type: 'line',
                data: {
                    labels: ['2022', '2023', '2024'],
                    datasets: [{
                        label: 'Cost-to-Income Ratio',
                        data: [46.4, 45.8, 45.2],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Revenue per Employee (AUD K)',
                        data: [458, 472, 485],
                        borderColor: '#764ba2',
                        backgroundColor: 'rgba(118, 75, 162, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            grid: {
                                drawOnChartArea: false,
                            },
                        },
                    },
                }
            });
        }

        // Cost Structure Chart
        const costCtx = document.getElementById('costStructureChart');
        if (costCtx && !this.charts.costStructure) {
            this.charts.costStructure = new Chart(costCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Personnel', 'Technology', 'Premises', 'Other'],
                    datasets: [{
                        data: [45, 25, 15, 15],
                        backgroundColor: [
                            '#667eea',
                            '#764ba2',
                            '#f093fb',
                            '#f5576c'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }

    initializeComparisonCharts() {
        // Peer Comparison Chart
        const comparisonCtx = document.getElementById('peerComparisonChart');
        if (comparisonCtx && !this.charts.peerComparison) {
            this.charts.peerComparison = new Chart(comparisonCtx, {
                type: 'radar',
                data: {
                    labels: ['ROE', 'NIM', 'CET1', 'Cost/Income', 'LCR'],
                    datasets: [{
                        label: 'NAB',
                        data: [14.2, 2.15, 12.8, 45.2, 125],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.2)',
                        pointBackgroundColor: '#667eea'
                    }, {
                        label: 'CBA',
                        data: [13.8, 2.08, 12.5, 44.8, 128],
                        borderColor: '#764ba2',
                        backgroundColor: 'rgba(118, 75, 162, 0.2)',
                        pointBackgroundColor: '#764ba2'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // Market Position Chart
        const marketCtx = document.getElementById('marketPositionChart');
        if (marketCtx && !this.charts.marketPosition) {
            this.charts.marketPosition = new Chart(marketCtx, {
                type: 'bar',
                data: {
                    labels: ['NAB', 'CBA', 'Westpac', 'ANZ'],
                    datasets: [{
                        label: 'Market Share (%)',
                        data: [18.5, 25.2, 22.1, 15.8],
                        backgroundColor: [
                            'rgba(102, 126, 234, 0.8)',
                            'rgba(118, 75, 162, 0.8)',
                            'rgba(240, 147, 251, 0.8)',
                            'rgba(245, 87, 108, 0.8)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 30
                        }
                    }
                }
            });
        }
    }

    initializeTrendsCharts() {
        // Historical Trends Chart
        const trendsCtx = document.getElementById('historicalTrendsChart');
        if (trendsCtx && !this.charts.historicalTrends) {
            this.charts.historicalTrends = new Chart(trendsCtx, {
                type: 'line',
                data: {
                    labels: ['2020', '2021', '2022', '2023', '2024'],
                    datasets: [{
                        label: 'Net Interest Income',
                        data: [18500, 20500, 22000, 23500, 24800],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Net Profit After Tax',
                        data: [6800, 7500, 8500, 8900, 9200],
                        borderColor: '#764ba2',
                        backgroundColor: 'rgba(118, 75, 162, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + (value / 1000) + 'B';
                                }
                            }
                        }
                    }
                }
            });
        }

        // Forecast Chart
        const forecastCtx = document.getElementById('forecastChart');
        if (forecastCtx && !this.charts.forecast) {
            this.charts.forecast = new Chart(forecastCtx, {
                type: 'line',
                data: {
                    labels: ['2024', '2025', '2026', '2027'],
                    datasets: [{
                        label: 'Actual',
                        data: [24800, null, null, null],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Forecast',
                        data: [24800, 26200, 27500, 28800],
                        borderColor: '#764ba2',
                        backgroundColor: 'rgba(118, 75, 162, 0.1)',
                        borderDash: [5, 5],
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + (value / 1000) + 'B';
                                }
                            }
                        }
                    }
                }
            });
        }
    }

    updateDashboard() {
        // Update metric cards with current data
        this.updateMetricCards();
        
        // Update charts with new data
        this.updateCharts();
    }

    updateMetricCards() {
        // Update overview metrics
        if (this.data.overview) {
            this.updateMetricCard('niiChart', this.data.overview.netInterestIncome);
            this.updateMetricCard('npatChart', this.data.overview.netProfitAfterTax);
            this.updateMetricCard('roeChart', this.data.overview.returnOnEquity);
            this.updateMetricCard('cet1Chart', this.data.overview.cet1Ratio);
        }
    }

    updateMetricCard(chartId, data) {
        const canvas = document.getElementById(chartId);
        if (canvas && data) {
            const ctx = canvas.getContext('2d');
            
            // Clear previous chart
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw mini trend chart
            const width = canvas.width;
            const height = canvas.height;
            const padding = 10;
            const chartWidth = width - 2 * padding;
            const chartHeight = height - 2 * padding;
            
            // Find min and max values for scaling
            const values = data.trend || [data.value];
            const min = Math.min(...values);
            const max = Math.max(...values);
            const range = max - min || 1;
            
            // Draw trend line
            ctx.beginPath();
            ctx.strokeStyle = '#667eea';
            ctx.lineWidth = 2;
            
            values.forEach((value, index) => {
                const x = padding + (index / (values.length - 1)) * chartWidth;
                const y = height - padding - ((value - min) / range) * chartHeight;
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
        }
    }

    updateCharts() {
        // Update all charts with new data
        Object.keys(this.charts).forEach(chartKey => {
            const chart = this.charts[chartKey];
            if (chart && chart.data) {
                chart.update();
            }
        });
    }

    updatePeerComparison() {
        const selectedPeers = Array.from(document.getElementById('peerSelect').selectedOptions)
            .map(option => option.value);
        
        if (selectedPeers.length > 0) {
            // Update peer comparison chart with selected peers
            this.loadPeerData(selectedPeers);
        }
    }

    async loadPeerData(peers) {
        // Load data for selected peers
        const peerData = {};
        
        for (const peer of peers) {
            try {
                const response = await fetch(`/api/extract?bank=${peer}&year=${this.currentYear || 2024}`);
                const data = await response.json();
                if (data.items) {
                    peerData[peer] = this.processPeerData(data.items);
                }
            } catch (error) {
                console.error(`Error loading data for ${peer}:`, error);
            }
        }
        
        this.updatePeerComparisonChart(peerData);
    }

    processPeerData(items) {
        const processed = {};
        items.forEach(item => {
            processed[item.standard_name] = parseFloat(item.value) || 0;
        });
        return processed;
    }

    updatePeerComparisonChart(peerData) {
        const chart = this.charts.peerComparison;
        if (chart) {
            // Update chart data with peer information
            const datasets = [];
            const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c'];
            
            Object.keys(peerData).forEach((peer, index) => {
                const data = peerData[peer];
                datasets.push({
                    label: peer.toUpperCase(),
                    data: [
                        data.roe || 0,
                        data.nim || 0,
                        data.cet1_ratio || 0,
                        data.cost_income_ratio || 0,
                        data.lcr || 0
                    ],
                    borderColor: colors[index % colors.length],
                    backgroundColor: colors[index % colors.length] + '20',
                    pointBackgroundColor: colors[index % colors.length]
                });
            });
            
            chart.data.datasets = datasets;
            chart.update();
        }
    }

    showLoading() {
        document.body.classList.add('loading');
    }

    hideLoading() {
        document.body.classList.remove('loading');
    }

    showError(message) {
        // Create and show error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #dc3545;
            color: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
        `;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BankDashboard();
});