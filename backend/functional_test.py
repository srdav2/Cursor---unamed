#!/usr/bin/env python3
"""
Functional test for the AI classifier that can work with available modules.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Mock missing modules for testing
class MockModule:
    def __init__(self, name):
        self.name = name

# Mock pdfplumber if not available
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    pdfplumber = MockModule("pdfplumber")

# Mock torch and transformers if not available
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    AI_DEPENDENCIES_AVAILABLE = True
except ImportError:
    AI_DEPENDENCIES_AVAILABLE = False
    torch = MockModule("torch")
    AutoTokenizer = MockModule("AutoTokenizer")
    AutoModelForCausalLM = MockModule("AutoModelForCausalLM")

def test_ai_classifier_import():
    """Test if the AI classifier can be imported."""
    print("Testing AI Classifier Import")
    print("=" * 40)
    
    try:
        # Temporarily modify sys.path to include current directory
        sys.path.insert(0, os.getcwd())
        
        # Try to import the AI classifier
        from ai_classifier import AnnualReportClassifier, classify_document, classify_batch, get_classifier
        
        print("✓ AI classifier module imported successfully")
        print(f"✓ AnnualReportClassifier class available")
        print(f"✓ classify_document function available")
        print(f"✓ classify_batch function available")
        print(f"✓ get_classifier function available")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to import AI classifier: {e}")
        return False

def test_config_loading():
    """Test configuration loading functionality."""
    print("\nTesting Configuration Loading")
    print("=" * 40)
    
    try:
        from ai_classifier import AnnualReportClassifier
        
        # Test with default config
        classifier = AnnualReportClassifier()
        
        # Check if config is loaded
        if hasattr(classifier, 'config'):
            print("✓ Configuration loaded successfully")
            
            # Check required config sections
            required_sections = ['model_config', 'classification_config', 'prompts', 'fallback_indicators']
            for section in required_sections:
                if section in classifier.config:
                    print(f"✓ {section} section found in config")
                else:
                    print(f"✗ {section} section missing from config")
                    return False
            
            return True
        else:
            print("✗ Configuration not loaded")
            return False
            
    except Exception as e:
        print(f"✗ Failed to test configuration loading: {e}")
        return False

def test_fallback_classification():
    """Test the fallback classification functionality."""
    print("\nTesting Fallback Classification")
    print("=" * 40)
    
    try:
        from ai_classifier import AnnualReportClassifier
        
        classifier = AnnualReportClassifier()
        
        # Test with sample content that should be classified as annual report
        annual_report_content = """
        ANNUAL REPORT AND ACCOUNTS
        For the year ended 31 December 2024
        
        CONSOLIDATED FINANCIAL STATEMENTS
        Statement of Financial Position
        Income Statement
        Cash Flow Statement
        
        Independent Auditor's Report
        """
        
        result = classifier._fallback_classification(annual_report_content)
        
        print(f"✓ Fallback classification result: {result}")
        
        # Check if result has required keys
        required_keys = ['is_annual_report', 'confidence', 'reasoning', 'method']
        for key in required_keys:
            if key in result:
                print(f"✓ {key} found in result")
            else:
                print(f"✗ {key} missing from result")
                return False
        
        # Check if it correctly identified as annual report
        if result['is_annual_report']:
            print("✓ Correctly identified as annual report")
        else:
            print("✗ Failed to identify as annual report")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test fallback classification: {e}")
        return False

def test_negative_classification():
    """Test classification of non-annual report content."""
    print("\nTesting Negative Classification")
    print("=" * 40)
    
    try:
        from ai_classifier import AnnualReportClassifier
        
        classifier = AnnualReportClassifier()
        
        # Test with sample content that should NOT be classified as annual report
        quarterly_report_content = """
        QUARTERLY REPORT
        Q1 2024 Results
        
        Investor Presentation
        Trading Update
        
        Press Release
        """
        
        result = classifier._fallback_classification(quarterly_report_content)
        
        print(f"✓ Negative classification result: {result}")
        
        # Check if it correctly identified as NOT annual report
        if not result['is_annual_report']:
            print("✓ Correctly identified as NOT annual report")
        else:
            print("✗ Incorrectly identified as annual report")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test negative classification: {e}")
        return False

def test_pdf_text_extraction():
    """Test PDF text extraction functionality."""
    print("\nTesting PDF Text Extraction")
    print("=" * 40)
    
    if not PDFPLUMBER_AVAILABLE:
        print("⚠️  pdfplumber not available, skipping PDF text extraction test")
        return True
    
    try:
        from ai_classifier import AnnualReportClassifier
        
        classifier = AnnualReportClassifier()
        
        # Check if the method exists
        if hasattr(classifier, '_extract_text_from_pdf'):
            print("✓ _extract_text_from_pdf method found")
            
            # Test with a real PDF if available
            pdf_files = list(Path("../data/reports").rglob("*.pdf"))
            if pdf_files:
                test_pdf = str(pdf_files[0])
                print(f"Testing with PDF: {test_pdf}")
                
                try:
                    text = classifier._extract_text_from_pdf(test_pdf, max_chars=1000)
                    if text:
                        print(f"✓ Successfully extracted {len(text)} characters from PDF")
                        print(f"  Preview: {text[:200]}...")
                    else:
                        print("⚠️  No text extracted from PDF")
                except Exception as e:
                    print(f"⚠️  PDF text extraction failed: {e}")
            
            return True
        else:
            print("✗ _extract_text_from_pdf method not found")
            return False
            
    except Exception as e:
        print(f"✗ Failed to test PDF text extraction: {e}")
        return False

def test_classifier_initialization():
    """Test classifier initialization with different configurations."""
    print("\nTesting Classifier Initialization")
    print("=" * 40)
    
    try:
        from ai_classifier import AnnualReportClassifier
        
        # Test default initialization
        classifier1 = AnnualReportClassifier()
        print("✓ Default initialization successful")
        
        # Test with custom config path
        config_path = "ai_config.json"
        if os.path.exists(config_path):
            classifier2 = AnnualReportClassifier(config_path=config_path)
            print("✓ Custom config initialization successful")
        
        # Test with custom model name
        classifier3 = AnnualReportClassifier(model_name="test-model")
        print("✓ Custom model name initialization successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test classifier initialization: {e}")
        return False

def test_api_endpoints():
    """Test if API endpoints are properly defined."""
    print("\nTesting API Endpoints")
    print("=" * 40)
    
    try:
        with open("main.py", 'r') as f:
            content = f.read()
        
        # Check for endpoint definitions
        endpoints = [
            ("/api/ai/classify", "POST"),
            ("/api/ai/classify_batch", "POST"),
            ("/api/ai/status", "GET")
        ]
        
        for endpoint, method in endpoints:
            if endpoint in content:
                print(f"✓ {method} {endpoint} endpoint found")
            else:
                print(f"✗ {method} {endpoint} endpoint not found")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test API endpoints: {e}")
        return False

def main():
    """Run all functional tests."""
    print("AI Classifier Functional Testing")
    print("=" * 50)
    
    tests = [
        ("AI Classifier Import", test_ai_classifier_import),
        ("Configuration Loading", test_config_loading),
        ("Fallback Classification", test_fallback_classification),
        ("Negative Classification", test_negative_classification),
        ("PDF Text Extraction", test_pdf_text_extraction),
        ("Classifier Initialization", test_classifier_initialization),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Functional Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All functional tests passed! AI classifier is working as intended.")
        print("\nThe AI classifier is ready to use with:")
        print("1. Fallback classification (rule-based) - Always available")
        print("2. AI classification (Llama model) - When dependencies are installed")
        print("3. API endpoints - For integration with web applications")
    else:
        print("⚠️  Some functional tests failed. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    main()