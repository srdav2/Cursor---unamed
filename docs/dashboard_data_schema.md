# Bank Financial Analytics Dashboard - Data Schema

## Overview

This document defines the comprehensive data schema required for the Bank Financial Analytics Dashboard. The schema covers all financial metrics, ratios, and data elements that need to be extracted from annual reports to power the interactive dashboards.

## Core Data Categories

### 1. Overview Metrics

**Primary financial indicators that provide a high-level view of bank performance.**

| Metric Name | Standard Name | Description | Unit | Frequency | Source Section |
|-------------|---------------|-------------|------|-----------|----------------|
| Net Interest Income | `net_interest_income` | Interest earned minus interest paid | Currency | Annual | Income Statement |
| Net Profit After Tax | `net_profit_after_tax` | Profit after all taxes and expenses | Currency | Annual | Income Statement |
| Return on Equity | `roe` | Net profit divided by shareholders' equity | Percentage | Annual | Calculated |
| CET1 Ratio | `cet1_ratio` | Common Equity Tier 1 capital ratio | Percentage | Annual | Capital Adequacy |

### 2. Profitability Analysis

**Metrics focused on revenue generation, margins, and profitability drivers.**

| Metric Name | Standard Name | Description | Unit | Frequency | Source Section |
|-------------|---------------|-------------|------|-----------|----------------|
| Net Interest Margin | `nim` | Net interest income as % of average interest-earning assets | Percentage | Annual | Calculated |
| Cost-to-Income Ratio | `cost_income_ratio` | Operating expenses as % of operating income | Percentage | Annual | Calculated |
| Operating Leverage | `operating_leverage` | Revenue growth vs cost growth ratio | Ratio | Annual | Calculated |
| Fee Income | `fee_income` | Non-interest income from fees and commissions | Currency | Annual | Income Statement |
| Trading Income | `trading_income` | Income from trading activities | Currency | Annual | Income Statement |
| Other Operating Income | `other_operating_income` | Other non-interest income | Currency | Annual | Income Statement |

### 3. Risk & Capital Management

**Capital adequacy, risk metrics, and regulatory compliance indicators.**

| Metric Name | Standard Name | Description | Unit | Frequency | Source Section |
|-------------|---------------|-------------|------|-----------|----------------|
| CET1 Ratio | `cet1_ratio` | Common Equity Tier 1 capital ratio | Percentage | Annual | Capital Adequacy |
| Total Capital Ratio | `total_capital_ratio` | Total capital as % of risk-weighted assets | Percentage | Annual | Capital Adequacy |
| Leverage Ratio | `leverage_ratio` | Tier 1 capital as % of total exposure | Percentage | Annual | Capital Adequacy |
| Liquidity Coverage Ratio | `lcr` | High-quality liquid assets as % of net cash outflows | Percentage | Annual | Liquidity |
| Net Stable Funding Ratio | `nsfr` | Available stable funding as % of required stable funding | Percentage | Annual | Liquidity |
| Non-Performing Loans | `npl_ratio` | Non-performing loans as % of total loans | Percentage | Annual | Credit Risk |
| Loan Loss Provisions | `loan_loss_provisions` | Provisions for credit losses | Currency | Annual | Income Statement |
| Credit Risk Weighted Assets | `credit_rwa` | Risk-weighted assets for credit risk | Currency | Annual | Capital Adequacy |

### 4. Liquidity Management

**Liquidity ratios, funding sources, and cash flow analysis.**

| Metric Name | Standard Name | Description | Unit | Frequency | Source Section |
|-------------|---------------|-------------|------|-----------|----------------|
| Loan-to-Deposit Ratio | `loan_deposit_ratio` | Total loans as % of total deposits | Percentage | Annual | Calculated |
| Wholesale Funding | `wholesale_funding` | Wholesale funding as % of total funding | Percentage | Annual | Funding |
| Customer Deposits | `customer_deposits` | Total customer deposits | Currency | Annual | Balance Sheet |
| Liquid Assets | `liquid_assets` | High-quality liquid assets | Currency | Annual | Balance Sheet |
| Net Cash from Operating Activities | `net_cash_operating` | Net cash flow from operating activities | Currency | Annual | Cash Flow |
| Net Cash from Investing Activities | `net_cash_investing` | Net cash flow from investing activities | Currency | Annual | Cash Flow |
| Net Cash from Financing Activities | `net_cash_financing` | Net cash flow from financing activities | Currency | Annual | Cash Flow |

### 5. Operational Efficiency

**Cost management, productivity metrics, and operational performance.**

| Metric Name | Standard Name | Description | Unit | Frequency | Source Section |
|-------------|---------------|-------------|------|-----------|----------------|
| Cost-to-Income Ratio | `cost_income_ratio` | Operating expenses as % of operating income | Percentage | Annual | Calculated |
| Revenue per Employee | `revenue_per_employee` | Total revenue divided by number of employees | Currency | Annual | Calculated |
| Digital Adoption | `digital_adoption` | Percentage of digital transactions | Percentage | Annual | Digital Metrics |
| Branch Network | `branch_count` | Number of physical branches | Count | Annual | Operations |
| Employee Count | `employee_count` | Total number of employees | Count | Annual | Operations |
| Technology Investment | `technology_investment` | Technology and digital investment | Currency | Annual | Operations |

### 6. Asset & Liability Management

**Balance sheet composition and asset-liability management.**

| Metric Name | Standard Name | Description | Unit | Frequency | Source Section |
|-------------|---------------|-------------|------|-----------|----------------|
| Total Assets | `total_assets` | Total assets | Currency | Annual | Balance Sheet |
| Total Liabilities | `total_liabilities` | Total liabilities | Currency | Annual | Balance Sheet |
| Total Equity | `total_equity` | Total shareholders' equity | Currency | Annual | Balance Sheet |
| Loans and Advances | `loans_and_advances` | Total loans and advances | Currency | Annual | Balance Sheet |
| Investment Securities | `investment_securities` | Investment securities portfolio | Currency | Annual | Balance Sheet |
| Cash and Equivalents | `cash_equivalents` | Cash and cash equivalents | Currency | Annual | Balance Sheet |
| Customer Deposits | `customer_deposits` | Customer deposits | Currency | Annual | Balance Sheet |
| Wholesale Funding | `wholesale_funding_amount` | Wholesale funding amount | Currency | Annual | Balance Sheet |

### 7. Market & Competitive Position

**Market share, competitive metrics, and industry positioning.**

| Metric Name | Standard Name | Description | Unit | Frequency | Source Section |
|-------------|---------------|-------------|------|-----------|----------------|
| Market Share | `market_share` | Market share in key segments | Percentage | Annual | Market Data |
| Customer Satisfaction | `customer_satisfaction` | Customer satisfaction score | Score | Annual | Customer Metrics |
| Brand Value | `brand_value` | Brand value assessment | Currency | Annual | Brand Metrics |
| Digital Banking Penetration | `digital_penetration` | Digital banking adoption rate | Percentage | Annual | Digital Metrics |
| Mobile Banking Users | `mobile_users` | Number of mobile banking users | Count | Annual | Digital Metrics |

### 8. Regulatory & Compliance

**Regulatory metrics and compliance indicators.**

| Metric Name | Standard Name | Description | Unit | Frequency | Source Section |
|-------------|---------------|-------------|------|-----------|----------------|
| Regulatory Capital | `regulatory_capital` | Total regulatory capital | Currency | Annual | Capital Adequacy |
| Risk-Weighted Assets | `risk_weighted_assets` | Total risk-weighted assets | Currency | Annual | Capital Adequacy |
| Capital Conservation Buffer | `capital_conservation_buffer` | Capital conservation buffer | Percentage | Annual | Capital Adequacy |
| Countercyclical Buffer | `countercyclical_buffer` | Countercyclical capital buffer | Percentage | Annual | Capital Adequacy |
| Systemic Risk Buffer | `systemic_risk_buffer` | Systemic risk buffer | Percentage | Annual | Capital Adequacy |

## Data Extraction Requirements

### Source Documents

1. **Annual Reports**
   - Income Statement
   - Balance Sheet
   - Cash Flow Statement
   - Notes to Financial Statements
   - Risk Management Section
   - Capital Adequacy Section
   - Liquidity Section

2. **Regulatory Filings**
   - Pillar 3 Reports
   - Regulatory Capital Reports
   - Liquidity Reports

3. **Supplementary Information**
   - Investor Presentations
   - Quarterly Reports
   - Sustainability Reports

### Data Quality Requirements

1. **Accuracy**
   - Source verification required
   - Cross-reference with multiple sources
   - Confidence scoring for extracted values

2. **Completeness**
   - Historical data for trend analysis
   - Peer comparison data
   - Industry benchmarks

3. **Timeliness**
   - Real-time updates when new reports are available
   - Quarterly updates for key metrics
   - Annual comprehensive updates

### Data Processing Rules

1. **Currency Conversion**
   - All amounts converted to reporting currency
   - Exchange rates from official sources
   - Historical rates for trend analysis

2. **Normalization**
   - Consistent units across all metrics
   - Standardized naming conventions
   - Harmonized calculation methodologies

3. **Validation**
   - Range checks for all metrics
   - Consistency checks across related metrics
   - Peer comparison validation

## Dashboard Integration

### Data Flow

1. **Extraction**
   - PDF parsing and text extraction
   - OCR for scanned documents
   - Manual verification for complex metrics

2. **Processing**
   - Data cleaning and normalization
   - Calculation of derived metrics
   - Quality assurance checks

3. **Storage**
   - Structured database storage
   - Version control for historical data
   - Backup and recovery procedures

4. **Presentation**
   - Real-time dashboard updates
   - Interactive visualizations
   - Export capabilities

### API Endpoints

```javascript
// Data retrieval endpoints
GET /api/metrics/{bank}/{year}           // Get all metrics for a bank/year
GET /api/metrics/{bank}/{year}/{metric}  // Get specific metric
GET /api/peers/{bank}/{year}             // Get peer comparison data
GET /api/trends/{bank}/{metric}          // Get historical trends
GET /api/forecasts/{bank}/{metric}       // Get forecast data

// Data management endpoints
POST /api/extract                        // Extract data from PDF
PUT /api/metrics/{bank}/{year}           // Update metrics
DELETE /api/metrics/{bank}/{year}        // Delete metrics
```

## Implementation Notes

1. **Scalability**
   - Support for multiple banks and regions
   - Efficient data storage and retrieval
   - Caching for performance optimization

2. **Security**
   - Data encryption at rest and in transit
   - Access control and authentication
   - Audit logging for all data changes

3. **Compliance**
   - GDPR compliance for data handling
   - Regulatory reporting requirements
   - Data retention policies

4. **Maintenance**
   - Regular data quality reviews
   - Schema version management
   - Automated testing and validation

## Future Enhancements

1. **Advanced Analytics**
   - Machine learning for trend prediction
   - Anomaly detection
   - Risk scoring models

2. **Integration**
   - Real-time market data feeds
   - External data sources
   - Third-party analytics tools

3. **User Experience**
   - Mobile-responsive design
   - Customizable dashboards
   - Advanced filtering and search

4. **Reporting**
   - Automated report generation
   - Scheduled email reports
   - Export to multiple formats