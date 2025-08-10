#!/usr/bin/env python3
"""
Simple Financial Statement Validator
====================================

This script validates if a document is likely a financial statement using:
1. Text pattern matching for financial indicators
2. Statistical analysis of financial terminology
3. Document structure analysis
4. Confidence scoring

Works with standard Python libraries - no external dependencies required.
"""

import re
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import Counter
from datetime import datetime

class FinancialDocumentValidator:
    """Validates if a document is likely a financial statement."""
    
    # High-confidence financial indicators
    FINANCIAL_INDICATORS = {
        "balance_sheet": [
            "balance sheet", "statement of financial position", "total assets", 
            "total liabilities", "shareholders equity", "equity attributable"
        ],
        "income_statement": [
            "income statement", "profit and loss", "revenue", "expenses", 
            "net income", "net profit", "operating income", "gross profit"
        ],
        "cash_flow": [
            "cash flow statement", "operating cash flow", "investing cash flow", 
            "financing cash flow", "net cash flow"
        ],
        "banking_metrics": [
            "net interest income", "net interest margin", "cost to income ratio",
            "return on equity", "return on assets", "cet1 ratio", "capital adequacy",
            "loan loss provision", "customer deposits", "loans and advances"
        ],
        "regulatory": [
            "audited", "consolidated", "financial statements", "annual report",
            "quarterly report", "interim report", "regulatory capital"
        ]
    }
    
    # Financial terminology frequency analysis
    FINANCIAL_TERMS = [
        "assets", "liabilities", "equity", "revenue", "expenses", "profit", "loss",
        "income", "cash", "debt", "capital", "investment", "loan", "deposit",
        "interest", "margin", "ratio", "percentage", "million", "billion",
        "audit", "consolidated", "financial", "statement", "report"
    ]
    
    # Common financial document structures
    DOCUMENT_STRUCTURES = [
        "executive summary", "financial highlights", "management discussion",
        "financial statements", "notes to financial statements", "auditor report",
        "directors report", "risk management", "corporate governance"
    ]
    
    def __init__(self):
        self.compiled_indicators = {}
        for category, terms in self.FINANCIAL_INDICATORS.items():
            self.compiled_indicators[category] = [
                re.compile(re.escape(term), re.IGNORECASE) for term in terms
            ]
        
        self.compiled_terms = [re.compile(re.escape(term), re.IGNORECASE) for term in self.FINANCIAL_TERMS]
        self.compiled_structures = [re.compile(re.escape(structure), re.IGNORECASE) for structure in self.DOCUMENT_STRUCTURES]

    def analyze_text_content(self, text: str) -> Dict[str, Any]:
        """Analyzes text content for financial statement indicators."""
        if not text:
            return {"error": "No text content provided"}
        
        text_lower = text.lower()
        results = {
            "total_length": len(text),
            "word_count": len(text.split()),
            "financial_indicators": {},
            "financial_terms_found": [],
            "document_structures": [],
            "confidence_score": 0.0,
            "analysis": {}
        }
        
        # Count financial indicators by category
        for category, patterns in self.compiled_indicators.items():
            count = 0
            found_terms = []
            for pattern in patterns:
                matches = pattern.findall(text_lower)
                if matches:
                    count += len(matches)
                    found_terms.extend(matches)
            results["financial_indicators"][category] = {
                "count": count,
                "terms_found": found_terms
            }
        
        # Count financial terminology
        for pattern in self.compiled_terms:
            matches = pattern.findall(text_lower)
            if matches:
                results["financial_terms_found"].extend(matches)
        
        # Find document structures
        for pattern in self.compiled_structures:
            matches = pattern.findall(text_lower)
            if matches:
                results["document_structures"].extend(matches)
        
        # Calculate confidence score
        total_indicators = sum(cat["count"] for cat in results["financial_indicators"].values())
        total_structures = len(results["document_structures"])
        total_terms = len(results["financial_terms_found"])
        
        # Weighted scoring system
        indicator_score = min(total_indicators * 0.3, 1.0)  # Max 30% from indicators
        structure_score = min(total_structures * 0.2, 0.4)   # Max 40% from structures
        term_score = min(total_terms * 0.01, 0.3)           # Max 30% from terminology
        
        results["confidence_score"] = indicator_score + structure_score + term_score
        results["confidence_score"] = min(results["confidence_score"], 1.0)
        
        # Analysis summary
        results["analysis"] = {
            "total_indicators": total_indicators,
            "total_structures": total_structures,
            "total_terms": total_terms,
            "indicator_score": indicator_score,
            "structure_score": structure_score,
            "term_score": term_score
        }
        
        return results

    def validate_financial_document(self, text: str) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Validates if text represents a financial document.
        Returns (is_financial, confidence, detailed_analysis)
        """
        analysis = self.analyze_text_content(text)
        
        if "error" in analysis:
            return False, 0.0, analysis
        
        confidence = analysis["confidence_score"]
        is_financial = confidence > 0.4  # Threshold for financial document
        
        return is_financial, confidence, analysis

    def extract_sample_text(self, file_path: str, max_chars: int = 50000) -> str:
        """Extracts sample text from a file (supports various formats)."""
        if not os.path.exists(file_path):
            return ""
        
        file_path = Path(file_path)
        
        # Try to read as text file first
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_chars)
                if content.strip():
                    return content
        except:
            pass
        
        # Try other encodings
        for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
            try:
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read(max_chars)
                    if content.strip():
                        return content
            except:
                continue
        
        return ""

def search_financial_databases():
    """Searches for existing financial statement databases and repositories."""
    
    print("=== Searching for Existing Financial Statement Solutions ===")
    print()
    
    # Known financial data sources
    financial_sources = {
        "SEC EDGAR": {
            "url": "https://www.sec.gov/edgar/searchedgar/companysearch",
            "description": "US Securities and Exchange Commission database with all public company filings",
            "coverage": "US public companies",
            "access": "Free public access"
        },
        "ASX Company Announcements": {
            "url": "https://www.asx.com.au/markets/trade-our-cash-market/company-announcements",
            "description": "Australian Securities Exchange company announcements and reports",
            "coverage": "Australian public companies",
            "access": "Free public access"
        },
        "Bank for International Settlements": {
            "url": "https://www.bis.org/statistics/",
            "description": "International banking statistics and financial data",
            "coverage": "Global banking sector",
            "access": "Free public access"
        },
        "World Bank Open Data": {
            "url": "https://data.worldbank.org/",
            "description": "Global financial and economic indicators",
            "coverage": "Global economic data",
            "access": "Free public access"
        },
        "IMF Data": {
            "url": "https://data.imf.org/",
            "description": "International Monetary Fund financial statistics",
            "coverage": "Global financial data",
            "access": "Free public access"
        }
    }
    
    print("🌐 Existing Financial Data Sources:")
    for name, info in financial_sources.items():
        print(f"\n📊 {name}")
        print(f"   URL: {info['url']}")
        print(f"   Description: {info['description']}")
        print(f"   Coverage: {info['coverage']}")
        print(f"   Access: {info['access']}")
    
    print("\n" + "="*60)
    print("💡 Recommendations for Financial Statement Analysis:")
    print("1. Use SEC EDGAR for US companies (most comprehensive)")
    print("2. Use ASX for Australian companies")
    print("3. Consider commercial data providers for bulk access:")
    print("   - Bloomberg Terminal")
    print("   - Reuters Eikon")
    print("   - S&P Capital IQ")
    print("   - Refinitiv")
    print("4. Build custom scrapers for specific bank websites")
    print("5. Use existing open-source financial analysis tools")

def analyze_local_documents():
    """Analyzes local documents to identify financial statements."""
    
    print("\n=== Local Document Analysis ===")
    print()
    
    validator = FinancialDocumentValidator()
    
    # Look for documents in common locations
    search_paths = [
        "data/downloads",
        "data/reports", 
        "data/docs",
        ".",
        "backend/reports"
    ]
    
    found_documents = []
    
    for search_path in search_paths:
        if os.path.exists(search_path):
            path = Path(search_path)
            for file_path in path.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in ['.txt', '.md', '.html', '.htm']:
                    found_documents.append(file_path)
    
    if not found_documents:
        print("No text documents found for analysis.")
        print("Consider converting PDFs to text or using OCR tools.")
        return
    
    print(f"Found {len(found_documents)} text documents for analysis:")
    print()
    
    for doc_path in found_documents[:5]:  # Analyze first 5
        print(f"📄 Analyzing: {doc_path.name}")
        
        try:
            sample_text = validator.extract_sample_text(str(doc_path))
            if sample_text:
                is_financial, confidence, analysis = validator.validate_financial_document(sample_text)
                
                status = "✅ Financial" if is_financial else "❌ Not Financial"
                print(f"   Status: {status}")
                print(f"   Confidence: {confidence:.1%}")
                
                if analysis.get("financial_indicators"):
                    total_indicators = sum(cat["count"] for cat in analysis["financial_indicators"].values())
                    print(f"   Financial Indicators: {total_indicators}")
                
                if analysis.get("document_structures"):
                    print(f"   Document Structures: {len(analysis['document_structures'])}")
                
                print()
            else:
                print(f"   ⚠️  Could not extract text content")
                print()
        except Exception as e:
            print(f"   ❌ Error analyzing document: {e}")
            print()

def main():
    """Main function to demonstrate financial document validation."""
    
    print("🔍 Financial Statement Identification & Analysis Tool")
    print("=" * 60)
    print()
    
    # Search for existing solutions
    search_financial_databases()
    
    # Analyze local documents
    analyze_local_documents()
    
    print("\n" + "="*60)
    print("🎯 Next Steps:")
    print("1. Download financial statements from official sources (SEC, ASX, etc.)")
    print("2. Use existing financial data APIs and databases")
    print("3. Build custom extractors for specific bank websites")
    print("4. Leverage existing open-source financial analysis tools")
    print("5. Consider commercial solutions for enterprise use")
    print()
    print("📚 Recommended Tools:")
    print("- SEC EDGAR API for US companies")
    print("- ASX API for Australian companies")
    print("- Python libraries: yfinance, pandas-datareader")
    print("- Financial data providers: Alpha Vantage, Quandl")
    print("- OCR tools: Tesseract, AWS Textract, Google Vision API")

if __name__ == "__main__":
    main()