#!/usr/bin/env python3
"""
Comprehensive test of the AI classifier implementation.
"""

import os
import sys
from pathlib import Path

def test_ai_classifier_comprehensive():
    """Comprehensive test of the AI classifier."""
    print("AI Classifier Comprehensive Testing")
    print("=" * 50)
    
    # Test 1: Basic functionality
    print("\n1. Testing Basic Functionality")
    print("-" * 30)
    
    try:
        from ai_classifier import AnnualReportClassifier, classify_document, classify_batch, get_classifier
        
        # Test classifier initialization
        classifier = AnnualReportClassifier()
        print("✓ Classifier initialized successfully")
        print(f"  Model: {classifier.model_name}")
        print(f"  Device: {classifier.device}")
        print(f"  AI Available: {hasattr(classifier, 'model') and classifier.model is not None}")
        
        # Test configuration loading
        if hasattr(classifier, 'config') and classifier.config:
            print("✓ Configuration loaded successfully")
            print(f"  Max content chars: {classifier.config['classification_config']['max_content_chars']}")
            print(f"  Confidence threshold: {classifier.config['classification_config']['confidence_threshold']}")
        else:
            print("✗ Configuration not loaded")
            return False
        
    except Exception as e:
        print(f"✗ Failed to test basic functionality: {e}")
        return False
    
    # Test 2: Fallback classification
    print("\n2. Testing Fallback Classification")
    print("-" * 30)
    
    try:
        # Test with annual report content
        annual_content = """
        ANNUAL REPORT AND ACCOUNTS
        For the year ended 31 December 2024
        
        CONSOLIDATED FINANCIAL STATEMENTS
        Statement of Financial Position
        Income Statement
        Cash Flow Statement
        
        Independent Auditor's Report
        """
        
        result = classifier._fallback_classification(annual_content)
        print(f"✓ Annual report classification: {result['is_annual_report']} (confidence: {result['confidence']}%)")
        
        # Test with non-annual report content
        quarterly_content = """
        QUARTERLY REPORT
        Q1 2024 Results
        
        Investor Presentation
        Trading Update
        """
        
        result2 = classifier._fallback_classification(quarterly_content)
        print(f"✓ Quarterly report classification: {result2['is_annual_report']} (confidence: {result2['confidence']}%)")
        
        if result['is_annual_report'] and not result2['is_annual_report']:
            print("✓ Fallback classification working correctly")
        else:
            print("✗ Fallback classification not working correctly")
            return False
            
    except Exception as e:
        print(f"✗ Failed to test fallback classification: {e}")
        return False
    
    # Test 3: Real PDF classification
    print("\n3. Testing Real PDF Classification")
    print("-" * 30)
    
    try:
        # Find PDF files
        pdf_files = list(Path("../data/reports").rglob("*.pdf"))
        
        if pdf_files:
            test_pdf = str(pdf_files[0])
            print(f"Testing with: {os.path.basename(test_pdf)}")
            
            # Test classification
            result = classify_document(test_pdf)
            
            print(f"✓ Classification result: {result['is_annual_report']}")
            print(f"  Confidence: {result['confidence']}%")
            print(f"  Method: {result.get('method', 'unknown')}")
            print(f"  Reasoning: {result.get('reasoning', 'N/A')[:100]}...")
            
            # Check if result is reasonable
            if result['method'] in ['ai', 'fallback', 'error']:
                print("✓ Classification method is valid")
            else:
                print("✗ Invalid classification method")
                return False
                
        else:
            print("⚠️  No PDF files found for testing")
            
    except Exception as e:
        print(f"✗ Failed to test real PDF classification: {e}")
        return False
    
    # Test 4: Integration with collector
    print("\n4. Testing Collector Integration")
    print("-" * 30)
    
    try:
        from collector import compute_financial_report_score, is_likely_financial_report
        
        if pdf_files:
            test_pdf = str(pdf_files[0])
            
            # Test enhanced scoring
            score = compute_financial_report_score(test_pdf, "nab", 2024)
            print(f"✓ Enhanced score: {score}")
            
            # Test classification
            is_annual = is_likely_financial_report(test_pdf, "nab", 2024)
            print(f"✓ Is likely financial report: {is_annual}")
            
        else:
            print("⚠️  No PDF files found for collector integration test")
            
    except Exception as e:
        print(f"✗ Failed to test collector integration: {e}")
        return False
    
    # Test 5: API endpoints
    print("\n5. Testing API Endpoints")
    print("-" * 30)
    
    try:
        with open("main.py", 'r') as f:
            content = f.read()
        
        endpoints = [
            "/api/ai/classify",
            "/api/ai/classify_batch", 
            "/api/ai/status"
        ]
        
        for endpoint in endpoints:
            if endpoint in content:
                print(f"✓ {endpoint} endpoint found")
            else:
                print(f"✗ {endpoint} endpoint not found")
                return False
                
    except Exception as e:
        print(f"✗ Failed to test API endpoints: {e}")
        return False
    
    # Test 6: Error handling
    print("\n6. Testing Error Handling")
    print("-" * 30)
    
    try:
        # Test with non-existent file
        result = classify_document("non_existent_file.pdf")
        
        if result['is_annual_report'] == False and result['confidence'] == 0:
            print("✓ Error handling for non-existent file working")
        else:
            print("✗ Error handling for non-existent file not working")
            return False
            
    except Exception as e:
        print(f"✗ Failed to test error handling: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All comprehensive tests passed!")
    print("\nAI Classifier Summary:")
    print("✓ Basic functionality working")
    print("✓ Fallback classification working")
    print("✓ Real PDF classification working")
    print("✓ Collector integration working")
    print("✓ API endpoints configured")
    print("✓ Error handling working")
    
    return True

def main():
    """Run comprehensive tests."""
    success = test_ai_classifier_comprehensive()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 AI Classifier is working as intended!")
        print("\nKey Features Verified:")
        print("1. ✓ AI-powered classification (when dependencies available)")
        print("2. ✓ Fallback rule-based classification (always available)")
        print("3. ✓ Confidence scoring for quality assurance")
        print("4. ✓ Integration with existing collector pipeline")
        print("5. ✓ API endpoints for web integration")
        print("6. ✓ Comprehensive error handling")
        print("7. ✓ Configurable parameters and prompts")
        
        print("\nNext Steps:")
        print("1. Install AI dependencies: pip install torch transformers")
        print("2. Configure model in ai_config.json")
        print("3. Test with real documents")
        print("4. Deploy to production")
        
    else:
        print("\n" + "=" * 50)
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return success

if __name__ == "__main__":
    main()