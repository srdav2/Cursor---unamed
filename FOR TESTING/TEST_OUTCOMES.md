# Annual Report Classification Test Outcomes

This document contains the correct expected outcomes for each test file in the FOR TESTING folder. These outcomes have been determined through manual analysis and should be used to validate the accuracy of any new LLM-based classification system.

## Test Files and Expected Outcomes

| File Name | Expected Outcome | Reasoning |
|-----------|------------------|-----------|
| `san_FY2017_Annual_Report.pdf` | **REJECT** | This is a remuneration report, not a complete annual report. It contains information about executive compensation, incentive plans, and long-term saving systems, but lacks the core financial statements (income statement, balance sheet, cash flow statement) required for a complete annual report. |
| `jpm_FY2023_Annual_Report.pdf` | **ACCEPT** | This is a complete annual report containing all required financial statements: consolidated statements of operations (income statement), consolidated balance sheets, consolidated statements of cash flows, consolidated statements of changes in stockholders' equity, and notes to consolidated financial statements. |
| `wbc_FY2023_Annual_Report.pdf` | **ACCEPT** | This is a complete annual report containing all required financial statements: consolidated income statement, consolidated balance sheet, consolidated statement of cash flows, consolidated statement of changes in equity, and notes to the financial statements. |
| `ms_FY2025_Annual_Report.pdf` | **REJECT** | This is a proxy statement, not an annual report. It contains information about shareholder proposals, corporate governance matters, and voting recommendations, but lacks the core financial statements required for a complete annual report. |
| `anz_FY2024_Annual_Report.pdf` | **ACCEPT** | This is a complete annual report containing all required financial statements: consolidated income statement, consolidated balance sheet, consolidated statement of cash flows, consolidated statement of changes in equity, and notes to the financial statements. |
| `barc_FY2023_Annual_Report.pdf` | **ACCEPT** | This is a complete annual report containing all required financial statements: consolidated income statement, consolidated balance sheet, consolidated statement of cash flows, consolidated statement of changes in equity, and notes to the financial statements. |
| `boc_FY2025_Annual_Report.pdf` | **REJECT** | This appears to be a summary or interim report, not a complete annual report. While it contains some financial information, it lacks the comprehensive financial statements and detailed notes required for a complete annual report. |

## Classification Criteria

A document should be classified as **ACCEPT** (Annual Report) if it contains ALL of the following:

1. **Income Statement** - Consolidated statement of comprehensive income, consolidated income statement, profit and loss account, consolidated statements of operations, consolidated statements of income, consolidated statements of earnings, or consolidated statement of profit or loss
2. **Balance Sheet** - Consolidated statement of financial position, consolidated balance sheet, consolidated statements of financial condition
3. **Cash Flow Statement** - Consolidated statement of cash flows, consolidated cash flow statement, consolidated statements of cash flows
4. **At least one of the following:**
   - **Equity Statement** - Consolidated statement of changes in equity, consolidated statements of changes in stockholders' equity
   - **Notes to Financial Statements** - Notes to the consolidated financial statements, notes to the financial statements, notes to consolidated financial statements

A document should be classified as **REJECT** if:

- It is primarily about remuneration, compensation, or executive pay
- It is an interim or quarterly report
- It is a presentation or summary
- It is missing any of the three core financial statements (income statement, balance sheet, cash flow statement)
- It is a proxy statement or circular
- It is a sustainability report, ESG report, or other non-financial report

## Notes for Testing

- The classification should be based on the presence of the required financial statements, not on the document title or general content
- Documents may contain additional information (remuneration, sustainability, etc.) but must contain the core financial statements to be accepted
- The financial statements may be named slightly differently across regions and accounting standards, but should be recognizable as the core financial statements
- Documents that are clearly not annual reports (proxy statements, interim reports, presentations) should be rejected even if they contain some financial information
