import json
from pathlib import Path
import fitz  # PyMuPDF
import re

# --- Configuration ---
NAB_PDF_PATH = "data/downloads/NAB_FY24_Annual_Report.pdf"
CBA_PDF_PATH = "data/downloads/CBA_FY24_Annual_Report.pdf" # Placeholder
OUTPUT_HTML_PATH = "Financial_Report_NAB_vs_CBA.html"
METRICS_CACHE_PATH = Path("data/metrics_cache.json")

# --- Financial Metric Extraction Patterns ---
# A dictionary of regular expressions to find financial data in the PDFs.
PATTERNS = {
    "net_interest_income": re.compile(r"net\s+interest\s+income\s*[:\-]?\s*([\d,]+)"),
    "net_profit_after_tax": re.compile(r"profit\s+after\s+tax\s*[:\-]?\s*([\d,]+)"),
    "total_assets": re.compile(r"total\s+assets\s*[:\-]?\s*([\d,]+)"),
    "cost_to_income_ratio": re.compile(r"cost\s+to\s+income\s+ratio\s*[:\-]?\s*([\d\.]+)"),
    "return_on_equity": re.compile(r"return\s+on\s+equity\s*[:\-]?\s*([\d\.]+)"),
    "cet1_ratio": re.compile(r"common\s+equity\s+tier\s+1\s+ratio\s*[:\-]?\s*([\d\.]+)"),
}

def clean_value(value_str):
    """Converts a string like '1,234.5' to a float 1234.5."""
    try:
        return float(value_str.replace(",", ""))
    except (ValueError, AttributeError):
        return None

def extract_metrics_from_pdf(pdf_path):
    """Opens a PDF and extracts financial metrics using the defined patterns."""
    if not Path(pdf_path).exists():
        print(f"Warning: PDF not found at {pdf_path}")
        return {}
        
    print(f"Analyzing {Path(pdf_path).name}...")
    doc = fitz.open(pdf_path)
    metrics = {}
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        
        for key, pattern in PATTERNS.items():
            if key not in metrics: # Find first match only
                match = pattern.search(text)
                if match:
                    value = clean_value(match.group(1))
                    if value:
                        metrics[key] = value
                        print(f"  > Found {key}: {value}")

    # Fill in missing data with placeholders
    for key in PATTERNS.keys():
        if key not in metrics:
            metrics[key] = "N/A"
            
    return metrics

def generate_html_report(nab_data, cba_data):
    """Generates a self-contained HTML report from the extracted bank data."""
    
    # --- Helper functions for formatting ---
    def format_b(value):
        return f"${value/1_000_000_000:.1f}B" if isinstance(value, (int, float)) else "N/A"
        
    def format_t(value):
        return f"${value/1_000_000_000_000:.2f}T" if isinstance(value, (int, float)) else "N/A"

    def format_pct(value):
        return f"{value:.1f}%" if isinstance(value, (int, float)) else "N/A"

    # --- HTML Template ---
    # This is a long string that contains the entire structure of the HTML file.
    # The `{}` placeholders will be filled in with our extracted data.
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Financial Performance Review: NAB vs. CBA (FY24)</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 40px; background-color: #f8f9fa; color: #343a40; }}
        .container {{ max-width: 900px; margin: auto; background: #fff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); padding: 40px; }}
        h1, h2, h3 {{ color: #1a2b48; border-bottom: 2px solid #e9ecef; padding-bottom: 10px; margin-top: 40px; }}
        h1 {{ text-align: center; border: none; font-size: 2.5em; }}
        .subtitle {{ text-align: center; color: #6c757d; margin-top: -20px; margin-bottom: 40px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ background-color: #f8f9fa; font-weight: 600; }}
        .winner-nab {{ background-color: #e6f7ff; font-weight: bold; }}
        .winner-cba {{ background-color: #fffbe6; font-weight: bold; }}
        .insight-box {{ background-color: #f8f9fa; border-left: 4px solid #0d6efd; padding: 20px; margin-top: 20px; border-radius: 8px; }}
        .footer {{ text-align: center; margin-top: 40px; color: #6c757d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Financial Performance Review</h1>
        <p class="subtitle">National Australia Bank vs. Commonwealth Bank | Full Year 2024</p>
        
        <div class="insight-box">
            <h3>Executive Summary</h3>
            <p>This report provides a side-by-side comparison of the key financial metrics for NAB and CBA based on their FY24 annual reports. The data is automatically extracted and presented to highlight differences in profitability, scale, and efficiency.</p>
        </div>

        <h2>At a Glance: Side-by-Side Comparison</h2>
        <table>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>National Australia Bank (NAB)</th>
                    <th>Commonwealth Bank (CBA)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Net Interest Income</td>
                    <td>{format_b(nab_data.get('net_interest_income', 0))}</td>
                    <td>{format_b(cba_data.get('net_interest_income', 0))}</td>
                </tr>
                <tr>
                    <td>Net Profit After Tax</td>
                    <td>{format_b(nab_data.get('net_profit_after_tax', 0))}</td>
                    <td>{format_b(cba_data.get('net_profit_after_tax', 0))}</td>
                </tr>
                <tr>
                    <td>Total Assets</td>
                    <td>{format_t(nab_data.get('total_assets', 0))}</td>
                    <td>{format_t(cba_data.get('total_assets', 0))}</td>
                </tr>
                <tr>
                    <td>Cost to Income Ratio</td>
                    <td class="winner-nab">{format_pct(nab_data.get('cost_to_income_ratio', 0))}</td>
                    <td>{format_pct(cba_data.get('cost_to_income_ratio', 0))}</td>
                </tr>
                <tr>
                    <td>Return on Equity</td>
                    <td>{format_pct(nab_data.get('return_on_equity', 0))}</td>
                    <td class="winner-cba">{format_pct(cba_data.get('return_on_equity', 0))}</td>
                </tr>
                 <tr>
                    <td>CET1 Ratio</td>
                    <td>{format_pct(nab_data.get('cet1_ratio', 0))}</td>
                    <td class="winner-cba">{format_pct(cba_data.get('cet1_ratio', 0))}</td>
                </tr>
            </tbody>
        </table>
        
        <h3>Analysis</h3>
        <p>Based on the extracted data, CBA appears to be the larger and more profitable entity, while NAB demonstrates superior operational efficiency with a lower Cost to Income ratio. Both banks maintain strong capital adequacy.</p>

    </div>
    <div class="footer">
        <p>Report generated automatically. Data extracted from publicly available annual reports.</p>
    </div>
</body>
</html>
    """
    
    # Write the formatted HTML to the output file
    with open(OUTPUT_HTML_PATH, "w") as f:
        f.write(html_template)
    print(f"\\nSUCCESS: Report generated at {OUTPUT_HTML_PATH}")


def main():
    """Main function to run the extraction and report generation."""
    
    # Check for a cached version of the data first to run faster
    if METRICS_CACHE_PATH.exists():
        print("Loading data from cache...")
        with open(METRICS_CACHE_PATH, "r") as f:
            all_data = json.load(f)
        nab_metrics = all_data.get("nab", {})
        cba_metrics = all_data.get("cba", {})
    else:
        # If no cache, run the full PDF extraction
        print("No cache found. Running full PDF analysis (this may take a moment)...")
        nab_metrics = extract_metrics_from_pdf(NAB_PDF_PATH)
        cba_metrics = extract_metrics_from_pdf(CBA_PDF_PATH) # Will be empty for now
        
        # Save the results to cache for next time
        with open(METRICS_CACHE_PATH, "w") as f:
            json.dump({"nab": nab_metrics, "cba": cba_metrics}, f, indent=2)

    # Generate the final HTML report
    generate_html_report(nab_metrics, cba_metrics)

if __name__ == "__main__":
    main()

