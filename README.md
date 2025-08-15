# Bank Performance Dashboard

A comprehensive financial analysis tool that automatically extracts and visualizes key metrics from bank annual reports.

## Quick Start

**Simply double-click `Start Dashboard.command` to launch the complete application.**

The launcher will:
- Set up the Python environment
- Start the backend server
- Open the dashboard in your browser
- Display real financial data from your bank reports

## Two Ways to Use

### 1. Full Application (Recommended)
- **Double-click `Start Dashboard.command`**
- Get real-time data extraction from PDF annual reports
- Full backend API integration
- Advanced features like AI classification and data validation

### 2. Static Mode
- **Open `index.html` directly in a browser**
- Works with sample data only
- No backend required
- Quick preview of dashboard features

## Features

- **Automated Data Extraction**: Extracts financial metrics from PDF annual reports
- **AI-Powered Classification**: Automatically validates document types
- **Interactive Dashboards**: Multiple specialized views for different analysis needs
- **Real Bank Data**: Works with actual annual reports from major banks
- **Bank Comparison**: Side-by-side analysis of different institutions
- **Trend Analysis**: Historical performance and projections

## Dashboard Views

1. **Overview** - Key financial metrics at a glance
2. **Profitability** - Detailed income and margin analysis  
3. **Risk & Capital** - Capital adequacy and risk metrics
4. **Liquidity** - Funding structure and liquidity analysis
5. **Efficiency** - Operational efficiency metrics
6. **Peer Comparison** - Benchmarking against industry peers
7. **Trends & Forecasts** - Historical performance and projections

## Bank Data

The system includes annual reports and extracted data for major banks:
- Commonwealth Bank of Australia (CBA)
- National Australia Bank (NAB)
- Westpac Banking Corporation (WBC)
- ANZ Banking Group (ANZ)
- And many international banks (JPM, MS, HSBC, etc.)

## Usage

1. **Start the application** using `Start Dashboard.command`
2. **Select a bank** from the dropdown menu
3. **Choose a year** for analysis
4. **Explore different dashboard views** using the navigation tabs
5. **Compare banks** using the peer comparison features

## Technical Architecture

- **Backend**: Python Flask server with PDF processing and AI classification
- **Frontend**: Self-contained HTML/CSS/JavaScript dashboard
- **Data Processing**: Automated extraction and standardization pipeline
- **AI Integration**: Document classification and validation

## Requirements

- Python 3.7+ (automatically handled by the launcher)
- Modern web browser
- macOS (launcher script optimized for Mac)

## Support

The application runs entirely locally on your machine with no external dependencies or data sharing.