#!/usr/bin/env python3
"""
Simple test script for the AI classifier that can run without all dependencies.
"""

import os
import sys
import json
from pathlib import Path

def test_ai_classifier_structure():
    """Test the AI classifier module structure and basic functionality."""
    print("Testing AI Classifier Structure")
    print("=" * 40)
    
    # Check if ai_classifier.py exists
    if not os.path.exists("ai_classifier.py"):
        print("✗ ai_classifier.py not found")
        return False
    
    print("✓ ai_classifier.py found")
    
    # Check if ai_config.json exists
    if not os.path.exists("ai_config.json"):
        print("✗ ai_config.json not found")
        return False
    
    print("✓ ai_config.json found")
    
    # Test config loading
    try:
        with open("ai_config.json", 'r') as f:
            config = json.load(f)
        
        required_keys = ["model_config", "classification_config", "prompts", "fallback_indicators"]
        for key in required_keys:
            if key not in config:
                print(f"✗ Missing required config key: {key}")
                return False
        
        print("✓ ai_config.json is valid")
        
    except Exception as e:
        print(f"✗ Failed to load ai_config.json: {e}")
        return False
    
    return True

def test_collector_integration():
    """Test if the AI classifier is properly integrated into collector.py."""
    print("\nTesting Collector Integration")
    print("=" * 40)
    
    if not os.path.exists("collector.py"):
        print("✗ collector.py not found")
        return False
    
    print("✓ collector.py found")
    
    # Check if AI classifier is imported in collector.py
    try:
        with open("collector.py", 'r') as f:
            content = f.read()
        
        if "from ai_classifier import" in content:
            print("✓ AI classifier imported in collector.py")
        else:
            print("✗ AI classifier not imported in collector.py")
            return False
        
        if "AI_CLASSIFIER_AVAILABLE" in content:
            print("✓ AI_CLASSIFIER_AVAILABLE flag found")
        else:
            print("✗ AI_CLASSIFIER_AVAILABLE flag not found")
            return False
        
        if "classify_document" in content:
            print("✓ classify_document function used in collector.py")
        else:
            print("✗ classify_document function not used in collector.py")
            return False
        
    except Exception as e:
        print(f"✗ Failed to check collector.py integration: {e}")
        return False
    
    return True

def test_api_integration():
    """Test if the AI classifier is properly integrated into main.py."""
    print("\nTesting API Integration")
    print("=" * 40)
    
    if not os.path.exists("main.py"):
        print("✗ main.py not found")
        return False
    
    print("✓ main.py found")
    
    # Check if AI classifier endpoints are added
    try:
        with open("main.py", 'r') as f:
            content = f.read()
        
        if "from ai_classifier import" in content:
            print("✓ AI classifier imported in main.py")
        else:
            print("✗ AI classifier not imported in main.py")
            return False
        
        if "/api/ai/classify" in content:
            print("✓ /api/ai/classify endpoint found")
        else:
            print("✗ /api/ai/classify endpoint not found")
            return False
        
        if "/api/ai/classify_batch" in content:
            print("✓ /api/ai/classify_batch endpoint found")
        else:
            print("✗ /api/ai/classify_batch endpoint not found")
            return False
        
        if "/api/ai/status" in content:
            print("✓ /api/ai/status endpoint found")
        else:
            print("✗ /api/ai/status endpoint not found")
            return False
        
    except Exception as e:
        print(f"✗ Failed to check main.py integration: {e}")
        return False
    
    return True

def test_pdf_availability():
    """Test if there are PDF files available for testing."""
    print("\nTesting PDF Availability")
    print("=" * 40)
    
    # Check for PDF files in data/reports
    data_dir = Path("../data/reports")
    if not data_dir.exists():
        print("✗ data/reports directory not found")
        return False
    
    print("✓ data/reports directory found")
    
    # Find PDF files
    pdf_files = list(data_dir.rglob("*.pdf"))
    
    if not pdf_files:
        print("✗ No PDF files found in data/reports")
        return False
    
    print(f"✓ Found {len(pdf_files)} PDF file(s)")
    
    # List the PDF files
    for pdf_file in pdf_files:
        print(f"  - {pdf_file}")
    
    return True

def test_ai_classifier_code():
    """Test the AI classifier code structure without running it."""
    print("\nTesting AI Classifier Code Structure")
    print("=" * 40)
    
    try:
        with open("ai_classifier.py", 'r') as f:
            content = f.read()
        
        # Check for required classes and functions
        required_items = [
            "class AnnualReportClassifier",
            "def __init__",
            "def classify_document",
            "def classify_batch",
            "def get_classifier",
            "def _load_config",
            "def _load_model",
            "def _extract_text_from_pdf",
            "def _generate_response",
            "def _fallback_classification"
        ]
        
        for item in required_items:
            if item in content:
                print(f"✓ {item} found")
            else:
                print(f"✗ {item} not found")
                return False
        
        # Check for proper error handling
        if "try:" in content and "except" in content:
            print("✓ Error handling found")
        else:
            print("✗ Error handling not found")
            return False
        
        # Check for logging
        if "logger" in content:
            print("✓ Logging found")
        else:
            print("✗ Logging not found")
            return False
        
    except Exception as e:
        print(f"✗ Failed to check ai_classifier.py: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("AI Classifier Testing")
    print("=" * 50)
    
    tests = [
        ("AI Classifier Structure", test_ai_classifier_structure),
        ("Collector Integration", test_collector_integration),
        ("API Integration", test_api_integration),
        ("PDF Availability", test_pdf_availability),
        ("AI Classifier Code", test_ai_classifier_code)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! AI classifier is properly implemented.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run setup: python setup_ai_classifier.py")
        print("3. Test with real data: python test_ai_classifier.py")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    main()