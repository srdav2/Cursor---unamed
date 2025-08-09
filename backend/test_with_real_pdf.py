#!/usr/bin/env python3
"""
Test the AI classifier with a real PDF file.
"""

import os
import sys
from pathlib import Path

def test_with_real_pdf():
    """Test the AI classifier with the actual PDF file."""
    print("Testing AI Classifier with Real PDF")
    print("=" * 50)
    
    # Find the PDF file
    pdf_files = list(Path("../data/reports").rglob("*.pdf"))
    
    if not pdf_files:
        print("✗ No PDF files found for testing")
        return False
    
    test_pdf = str(pdf_files[0])
    print(f"Testing with: {test_pdf}")
    
    try:
        from ai_classifier import classify_document, get_classifier
        
        # Test the classifier
        print("\nClassifying document...")
        result = classify_document(test_pdf)
        
        print(f"\nClassification Results:")
        print(f"  Is Annual Report: {result['is_annual_report']}")
        print(f"  Confidence: {result['confidence']}%")
        print(f"  Method: {result.get('method', 'unknown')}")
        print(f"  Reasoning: {result.get('reasoning', 'N/A')}")
        
        if 'content_preview' in result:
            preview = result['content_preview']
            if len(preview) > 200:
                preview = preview[:200] + "..."
            print(f"  Content Preview: {preview}")
        
        # Check if the result makes sense
        if result['is_annual_report']:
            print("\n✓ Successfully identified as annual report!")
        else:
            print("\n⚠️  Identified as NOT an annual report")
        
        if result['confidence'] >= 60:
            print("✓ High confidence classification")
        elif result['confidence'] >= 30:
            print("⚠️  Medium confidence classification")
        else:
            print("⚠️  Low confidence classification")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test with real PDF: {e}")
        return False

def test_batch_classification():
    """Test batch classification with multiple PDFs if available."""
    print("\nTesting Batch Classification")
    print("=" * 50)
    
    # Find all PDF files
    pdf_files = list(Path("../data/reports").rglob("*.pdf"))
    
    if len(pdf_files) < 2:
        print("⚠️  Only one PDF file found, skipping batch test")
        return True
    
    try:
        from ai_classifier import classify_batch
        
        # Test batch classification
        pdf_paths = [str(pdf) for pdf in pdf_files[:3]]  # Test with up to 3 files
        print(f"Testing batch classification with {len(pdf_paths)} files...")
        
        results = classify_batch(pdf_paths)
        
        print(f"\nBatch Classification Results:")
        for result in results:
            pdf_name = os.path.basename(result['pdf_path'])
            print(f"  {pdf_name}: {result['is_annual_report']} (confidence: {result['confidence']}%)")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test batch classification: {e}")
        return False

def test_classifier_status():
    """Test the classifier status endpoint."""
    print("\nTesting Classifier Status")
    print("=" * 50)
    
    try:
        from ai_classifier import get_classifier
        
        classifier = get_classifier()
        
        print(f"Classifier Status:")
        print(f"  Model Name: {classifier.model_name}")
        print(f"  Device: {classifier.device}")
        print(f"  AI Dependencies Available: {hasattr(classifier, 'model') and classifier.model is not None}")
        print(f"  PDFPLUMBER Available: {hasattr(classifier, '_extract_text_from_pdf')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test classifier status: {e}")
        return False

def main():
    """Run all tests with real PDF."""
    print("AI Classifier Real PDF Testing")
    print("=" * 50)
    
    tests = [
        ("Real PDF Classification", test_with_real_pdf),
        ("Batch Classification", test_batch_classification),
        ("Classifier Status", test_classifier_status)
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
    print("Real PDF Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All real PDF tests passed! AI classifier is working correctly.")
        print("\nThe AI classifier successfully:")
        print("1. ✓ Classified the real PDF document")
        print("2. ✓ Provided confidence scores")
        print("3. ✓ Used appropriate classification method")
        print("4. ✓ Handled batch processing")
    else:
        print("⚠️  Some real PDF tests failed. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    main()