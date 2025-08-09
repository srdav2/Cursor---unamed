#!/usr/bin/env python3
"""
Test script for the AI-powered annual report classifier.
"""

import os
import sys
import logging
from pathlib import Path

# Add the backend directory to the path
sys.path.append(os.path.dirname(__file__))

from ai_classifier import classify_document, classify_batch, get_classifier

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_classifier():
    """Test the AI classifier with sample documents."""
    
    # Test single document classification
    print("Testing AI classifier...")
    
    # Check if we have any PDF files in the data directory
    data_dir = Path("data/reports")
    if not data_dir.exists():
        print(f"Data directory {data_dir} not found. Creating test structure...")
        data_dir.mkdir(parents=True, exist_ok=True)
        print("Please place some PDF files in the data/reports directory to test.")
        return
    
    # Find PDF files
    pdf_files = list(data_dir.rglob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in data/reports directory.")
        print("Please add some PDF files to test the classifier.")
        return
    
    print(f"Found {len(pdf_files)} PDF files to test.")
    
    # Test single document classification
    if pdf_files:
        test_pdf = str(pdf_files[0])
        print(f"\nTesting single document classification: {test_pdf}")
        
        try:
            result = classify_document(test_pdf)
            print(f"Classification result: {result}")
        except Exception as e:
            print(f"Error classifying {test_pdf}: {e}")
    
    # Test batch classification (first 3 files)
    if len(pdf_files) > 1:
        test_pdfs = [str(p) for p in pdf_files[:3]]
        print(f"\nTesting batch classification with {len(test_pdfs)} files...")
        
        try:
            results = classify_batch(test_pdfs)
            for result in results:
                print(f"  {result['pdf_path']}: {result['is_annual_report']} (confidence: {result['confidence']}%)")
        except Exception as e:
            print(f"Error in batch classification: {e}")

def test_classifier_status():
    """Test the classifier status and availability."""
    print("\nTesting classifier status...")
    
    try:
        classifier = get_classifier()
        print(f"Classifier initialized: {classifier is not None}")
        print(f"Model name: {classifier.model_name}")
        print(f"Device: {classifier.device}")
        print(f"AI dependencies available: {hasattr(classifier, 'model') and classifier.model is not None}")
    except Exception as e:
        print(f"Error getting classifier: {e}")

if __name__ == "__main__":
    print("AI Classifier Test Script")
    print("=" * 50)
    
    test_classifier_status()
    test_classifier()
    
    print("\nTest completed.")