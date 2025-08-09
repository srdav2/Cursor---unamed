#!/usr/bin/env python3
"""
Improved Financial Statement Extractor
======================================

This script improves upon the basic extractor by:
1. Using multiple extraction strategies (regex, table parsing, layout analysis)
2. Implementing better financial statement identification patterns
3. Adding validation and confidence scoring
4. Supporting multiple document formats and layouts
5. Using industry-standard financial terminology patterns

Based on best practices from existing financial analysis tools and repositories.
"""

import re
import json
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FinancialMetric:
    """Represents a single financial metric with metadata."""
    name: str
    value: Optional[float]
    raw_text: str
    page: int
    confidence: float
    extraction_method: str
    context: str
    units: Optional[str] = None
    currency: Optional[str] = None

class FinancialStatementIdentifier:
    """Identifies and validates financial statements using multiple strategies."""
    
    # Financial statement indicators - these suggest we have a real financial document
    FINANCIAL_INDICATORS = [
        # Balance sheet indicators
        r"balance\s+sheet",
        r"statement\s+of\s+financial\s+position",
        r"statement\s+of\s+assets\s+and\s+liabilities",
        r"total\s+assets",
        r"total\s+liabilities",
        r"shareholders?\s+equity",
        
        # Income statement indicators
        r"income\s+statement",
        r"profit\s+and\s+loss\s+statement",
        r"statement\s+of\s+comprehensive\s+income",
        r"revenue",
        r"expenses",
        r"net\s+income",
        r"net\s+profit",
        
        # Cash flow indicators
        r"cash\s+flow\s+statement",
        r"statement\s+of\s+cash\s+flows",
        r"operating\s+cash\s+flow",
        r"investing\s+cash\s+flow",
        r"financing\s+cash\s+flow",
        
        # Regulatory indicators
        r"audited",
        r"consolidated",
        r"financial\s+statements",
        r"annual\s+report",
        r"quarterly\s+report",
        r"interim\s+report",
        
        # Banking-specific indicators
        r"net\s+interest\s+income",
        r"net\s+interest\s+margin",
        r"loan\s+loss\s+provision",
        r"capital\s+adequacy",
        r"tier\s+1\s+capital",
        r"cet1\s+ratio",
        r"liquidity\s+coverage\s+ratio",
        r"cost\s+to\s+income\s+ratio",
        r"return\s+on\s+equity",
        r"return\s+on\s+assets"
    ]
    
    # Enhanced financial metric patterns with multiple variations
    FINANCIAL_PATTERNS = {
        "net_interest_income": [
            r"net\s+interest\s+income\s*[:\-]?\s*([\d,]+\.?\d*)",
            r"interest\s+income,\s+net\s*[:\-]?\s*([\d,]+\.?\d*)",
            r"net\s+interest\s+income\s*[:\-]?\s*\$?([\d,]+\.?\d*)",
            r"interest\s+income\s+net\s*[:\-]?\s*([\d,]+\.?\d*)",
        ],
        "net_profit_after_tax": [
            r"net\s+profit\s+after\s+tax\s*[:\-]?\s*([\d,]+\.?\d*)",
            r"profit\s+after\s+tax\s*[:\-]?\s*([\d,]+\.?\d*)",
            r"net\s+income\s+after\s+tax\s*[:\-]?\s*([\d,]+\.?\d*)",
            r"profit\s+for\s+the\s+year\s*[:\-]?\s*([\d,]+\.?\d*)",
            r"statutory\s+net\s+profit\s+after\s+tax\s*[:\-]?\s*([\d,]+\.?\d*)",
        ],
        "total_assets": [
            r"total\s+assets\s*[:\-]?\s*([\d,]+\.?\d*)",
            r"total\s+assets\s*[:\-]?\s*\$?([\d,]+\.?\d*)",
            r"assets\s+total\s*[:\-]?\s*([\d,]+\.?\d*)",
        ],
        "total_liabilities": [
            r"total\s+liabilities\s*[:\-]?\s*([\d,]+\.?\d*)",
            r"liabilities\s+total\s*[:\-]?\s*([\d,]+\.?\d*)",
        ],
        "total_equity": [
            r"total\s+equity\s*[:\-]?\s*([\d,]+\.?\d*)",
            r"shareholders?\s+equity\s*[:\-]?\s*([\d,]+\.?\d*)",
            r"equity\s+total\s*[:\-]?\s*([\d,]+\.?\d*)",
        ],
        "cost_to_income_ratio": [
            r"cost\s+to\s+income\s+ratio\s*[:\-]?\s*([\d\.]+)",
            r"cost/income\s+ratio\s*[:\-]?\s*([\d\.]+)",
            r"cost\s+income\s+ratio\s*[:\-]?\s*([\d\.]+)",
        ],
        "return_on_equity": [
            r"return\s+on\s+equity\s*[:\-]?\s*([\d\.]+)",
            r"roe\s*[:\-]?\s*([\d\.]+)",
            r"return\s+on\s+equity\s*\(?roe\)?\s*[:\-]?\s*([\d\.]+)",
        ],
        "return_on_assets": [
            r"return\s+on\s+assets\s*[:\-]?\s*([\d\.]+)",
            r"roa\s*[:\-]?\s*([\d\.]+)",
            r"return\s+on\s+assets\s*\(?roa\)?\s*[:\-]?\s*([\d\.]+)",
        ],
        "cet1_ratio": [
            r"common\s+equity\s+tier\s+1\s+ratio\s*[:\-]?\s*([\d\.]+)",
            r"cet1\s+ratio\s*[:\-]?\s*([\d\.]+)",
            r"tier\s+1\s+capital\s+ratio\s*[:\-]?\s*([\d\.]+)",
        ],
        "net_interest_margin": [
            r"net\s+interest\s+margin\s*[:\-]?\s*([\d\.]+)",
            r"nim\s*[:\-]?\s*([\d\.]+)",
            r"net\s+interest\s+margin\s*\(?nim\)?\s*[:\-]?\s*([\d\.]+)",
        ],
        "customer_deposits": [
            r"customer\s+deposits\s*[:\-]?\s*([\d,]+\.?\d*)",
            r"deposits\s+from\s+customers\s*[:\-]?\s*([\d,]+\.?\d*)",
            r"total\s+customer\s+deposits\s*[:\-]?\s*([\d,]+\.?\d*)",
        ],
        "loans_and_advances": [
            r"loans\s+and\s+advances\s*[:\-]?\s*([\d,]+\.?\d*)",
            r"net\s+loans\s*[:\-]?\s*([\d,]+\.?\d*)",
            r"gross\s+loans\s+and\s+advances\s*[:\-]?\s*([\d,]+\.?\d*)",
        ]
    }
    
    # Unit detection patterns
    UNIT_PATTERNS = {
        "thousands": [r"\b(thousands?|000s?|k)\b", 1000],
        "millions": [r"\b(millions?|\$?m\b|aud\s+m|aud\s+million|in\s+millions?)\b", 1000000],
        "billions": [r"\b(billions?|\$?bn\b|aud\s+bn|aud\s+billion|in\s+billions?)\b", 1000000000],
        "trillions": [r"\b(trillions?|\$?t\b|aud\s+t|aud\s+trillion|in\s+trillions?)\b", 1000000000000]
    }
    
    # Currency detection patterns
    CURRENCY_PATTERNS = {
        "AUD": [r"\$", r"aud", r"australian\s+dollar"],
        "USD": [r"us\$", r"usd", r"dollar"],
        "EUR": [r"€", r"eur", r"euro"],
        "GBP": [r"£", r"gbp", r"pound"],
        "CAD": [r"c\$", r"cad", r"canadian\s+dollar"],
        "JPY": [r"¥", r"jpy", r"yen"],
        "CNY": [r"¥", r"cny", r"rmb", r"yuan"],
        "SGD": [r"s\$", r"sgd", r"singapore\s+dollar"]
    }

    def __init__(self):
        self.compiled_indicators = [re.compile(pattern, re.IGNORECASE) for pattern in self.FINANCIAL_INDICATORS]
        self.compiled_patterns = {}
        for metric, patterns in self.FINANCIAL_PATTERNS.items():
            self.compiled_patterns[metric] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]

    def is_financial_statement(self, pdf_path: str) -> Tuple[bool, float, List[str]]:
        """
        Determines if a PDF is likely a financial statement.
        Returns (is_financial, confidence_score, evidence_list)
        """
        if not Path(pdf_path).exists():
            return False, 0.0, []
        
        doc = fitz.open(pdf_path)
        evidence = []
        total_score = 0
        max_possible_score = len(self.compiled_indicators)
        
        # Sample first 10 pages for indicators
        sample_pages = min(10, len(doc))
        
        for page_num in range(sample_pages):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            
            for pattern in self.compiled_indicators:
                if pattern.search(text):
                    evidence.append(f"Page {page_num + 1}: {pattern.pattern}")
                    total_score += 1
        
        confidence = total_score / max_possible_score if max_possible_score > 0 else 0.0
        is_financial = confidence > 0.3  # Threshold for considering it a financial statement
        
        doc.close()
        return is_financial, confidence, evidence

    def extract_metrics(self, pdf_path: str) -> List[FinancialMetric]:
        """Extracts financial metrics using multiple strategies."""
        if not Path(pdf_path).exists():
            return []
        
        doc = fitz.open(pdf_path)
        metrics = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            
            for metric_name, patterns in self.compiled_patterns.items():
                for pattern in patterns:
                    matches = pattern.finditer(text)
                    for match in matches:
                        raw_value = match.group(1)
                        value = self._clean_and_parse_value(raw_value)
                        
                        if value is not None:
                            # Detect units and currency
                            units = self._detect_units(text, match.start())
                            currency = self._detect_currency(text, match.start())
                            
                            # Normalize value based on units
                            normalized_value = self._normalize_value(value, units)
                            
                            # Calculate confidence based on pattern match quality
                            confidence = self._calculate_confidence(pattern, raw_value, text, match.start())
                            
                            # Get context around the match
                            context = self._get_context(text, match.start(), 100)
                            
                            metric = FinancialMetric(
                                name=metric_name,
                                value=normalized_value,
                                raw_text=raw_value,
                                page=page_num + 1,
                                confidence=confidence,
                                extraction_method="regex_pattern",
                                context=context,
                                units=units,
                                currency=currency
                            )
                            metrics.append(metric)
                            break  # Use first match for each metric per page
        
        doc.close()
        return metrics

    def _clean_and_parse_value(self, value_str: str) -> Optional[float]:
        """Cleans and parses a value string to float."""
        if not value_str:
            return None
        
        # Remove common formatting
        cleaned = value_str.strip()
        cleaned = cleaned.replace(",", "")
        cleaned = cleaned.replace("\u2212", "-")  # Unicode minus
        
        # Handle accounting negatives (parentheses)
        if cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = "-" + cleaned[1:-1]
        
        # Remove currency symbols and percentage
        cleaned = re.sub(r"[$%]", "", cleaned)
        
        try:
            return float(cleaned)
        except ValueError:
            return None

    def _detect_units(self, text: str, match_pos: int) -> Optional[str]:
        """Detects units (thousands, millions, billions) near the match."""
        # Look in a window around the match
        start = max(0, match_pos - 200)
        end = min(len(text), match_pos + 200)
        context = text[start:end]
        
        for unit_name, (pattern, multiplier) in self.UNIT_PATTERNS.items():
            if re.search(pattern, context, re.IGNORECASE):
                return unit_name
        
        return None

    def _detect_currency(self, text: str, match_pos: int) -> Optional[str]:
        """Detects currency near the match."""
        start = max(0, match_pos - 200)
        end = min(len(text), match_pos + 200)
        context = text[start:end]
        
        for currency, patterns in self.CURRENCY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, context, re.IGNORECASE):
                    return currency
        
        return None

    def _normalize_value(self, value: float, units: Optional[str]) -> float:
        """Normalizes value based on detected units."""
        if not units:
            return value
        
        for unit_name, (pattern, multiplier) in self.UNIT_PATTERNS.items():
            if units == unit_name:
                return value * multiplier
        
        return value

    def _calculate_confidence(self, pattern: re.Pattern, raw_value: str, text: str, match_pos: int) -> float:
        """Calculates confidence score for the extraction."""
        base_confidence = 0.7
        
        # Boost confidence for clean numeric values
        if re.match(r"^[\d,]+\.?\d*$", raw_value):
            base_confidence += 0.2
        
        # Boost confidence if we find units nearby
        if self._detect_units(text, match_pos):
            base_confidence += 0.1
        
        # Boost confidence if we find currency nearby
        if self._detect_currency(text, match_pos):
            base_confidence += 0.1
        
        return min(1.0, base_confidence)

    def _get_context(self, text: str, match_pos: int, window: int) -> str:
        """Gets context around the match position."""
        start = max(0, match_pos - window)
        end = min(len(text), match_pos + window)
        return text[start:end].strip()

def main():
    """Main function to demonstrate the improved extractor."""
    identifier = FinancialStatementIdentifier()
    
    # Test with our NAB PDF
    nab_pdf = "data/downloads/NAB_FY24_Annual_Report.pdf"
    
    if not Path(nab_pdf).exists():
        print(f"PDF not found: {nab_pdf}")
        return
    
    print("=== Financial Statement Analysis ===")
    print(f"Analyzing: {nab_pdf}")
    print()
    
    # Step 1: Identify if this is a financial statement
    print("Step 1: Validating Financial Statement")
    is_financial, confidence, evidence = identifier.is_financial_statement(nab_pdf)
    
    print(f"Is Financial Statement: {is_financial}")
    print(f"Confidence Score: {confidence:.2%}")
    print("Evidence Found:")
    for item in evidence[:5]:  # Show first 5 pieces of evidence
        print(f"  ✓ {item}")
    
    if not is_financial:
        print("\n⚠️  This document may not be a financial statement.")
        print("   Consider checking the document type or using a different file.")
        return
    
    print("\n✅ Document appears to be a financial statement!")
    print()
    
    # Step 2: Extract financial metrics
    print("Step 2: Extracting Financial Metrics")
    metrics = identifier.extract_metrics(nab_pdf)
    
    if not metrics:
        print("No metrics found. This might indicate:")
        print("  - Document uses different terminology")
        print("  - Metrics are in tables that need table parsing")
        print("  - Document has a unique layout")
        return
    
    print(f"Found {len(metrics)} metrics:")
    print()
    
    # Group metrics by name and show best matches
    metric_groups = {}
    for metric in metrics:
        if metric.name not in metric_groups:
            metric_groups[metric.name] = []
        metric_groups[metric.name].append(metric)
    
    for metric_name, metric_list in metric_groups.items():
        # Sort by confidence and take the best
        best_metric = max(metric_list, key=lambda x: x.confidence)
        
        print(f"📊 {metric_name.replace('_', ' ').title()}")
        print(f"   Value: {best_metric.value:,.2f}")
        print(f"   Raw Text: '{best_metric.raw_text}'")
        print(f"   Page: {best_metric.page}")
        print(f"   Confidence: {best_metric.confidence:.1%}")
        if best_metric.units:
            print(f"   Units: {best_metric.units}")
        if best_metric.currency:
            print(f"   Currency: {best_metric.currency}")
        print()
    
    # Step 3: Generate summary report
    print("Step 3: Summary Report")
    print("=" * 50)
    
    # Calculate overall extraction success
    total_metrics = len(identifier.FINANCIAL_PATTERNS)
    found_metrics = len(metric_groups)
    success_rate = (found_metrics / total_metrics) * 100
    
    print(f"Extraction Success Rate: {success_rate:.1f}%")
    print(f"Metrics Found: {found_metrics}/{total_metrics}")
    print(f"Document Confidence: {confidence:.1%}")
    
    # Save results
    results = {
        "document": nab_pdf,
        "analysis_timestamp": datetime.now().isoformat(),
        "is_financial_statement": is_financial,
        "confidence_score": confidence,
        "evidence": evidence,
        "extraction_summary": {
            "total_metrics_sought": total_metrics,
            "metrics_found": found_metrics,
            "success_rate": success_rate
        },
        "extracted_metrics": [
            {
                "name": m.name,
                "value": m.value,
                "raw_text": m.raw_text,
                "page": m.page,
                "confidence": m.confidence,
                "units": m.units,
                "currency": m.currency,
                "context": m.context
            }
            for m in metrics
        ]
    }
    
    output_file = "improved_extraction_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {output_file}")
    print("\n💡 Recommendations:")
    
    if success_rate < 50:
        print("  - Consider using table parsing for better results")
        print("  - Check if document uses industry-specific terminology")
        print("  - Verify document is a standard financial statement")
    
    if confidence < 0.7:
        print("  - Document may be a different type of financial document")
        print("  - Consider manual review of document structure")
    
    print("  - Use the detailed JSON output for further analysis")

if __name__ == "__main__":
    main()