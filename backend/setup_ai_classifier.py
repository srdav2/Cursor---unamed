#!/usr/bin/env python3
"""
Setup script for the AI-powered annual report classifier.
This script helps users configure and test the AI classifier.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if AI dependencies are available."""
    print("Checking AI dependencies...")
    
    dependencies = {
        "torch": False,
        "transformers": False,
        "accelerate": False,
        "sentencepiece": False
    }
    
    for dep in dependencies:
        try:
            __import__(dep)
            dependencies[dep] = True
            print(f"✓ {dep} - Available")
        except ImportError:
            print(f"✗ {dep} - Not available")
    
    all_available = all(dependencies.values())
    
    if not all_available:
        print("\nMissing dependencies. Install them with:")
        print("pip install torch transformers accelerate sentencepiece")
        print("\nOr install all dependencies with:")
        print("pip install -r requirements.txt")
    
    return all_available

def check_model_availability():
    """Check if the Llama model is available."""
    print("\nChecking model availability...")
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        model_name = "meta-llama/Llama-2-7b-chat-hf"
        print(f"Checking model: {model_name}")
        
        # Try to load tokenizer (this will download if not available)
        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        print("✓ Tokenizer loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Model not available: {e}")
        print("\nTo use the AI classifier, you need to:")
        print("1. Have a HuggingFace account")
        print("2. Request access to Llama-2 models at: https://huggingface.co/meta-llama/Llama-2-7b-chat-hf")
        print("3. Login with: huggingface-cli login")
        print("4. Download the model: huggingface-cli download meta-llama/Llama-2-7b-chat-hf")
        
        return False

def create_sample_config():
    """Create a sample configuration file."""
    config_path = Path("ai_config.json")
    
    if config_path.exists():
        print(f"Configuration file already exists at {config_path}")
        return
    
    sample_config = {
        "model_config": {
            "model_name": "meta-llama/Llama-2-7b-chat-hf",
            "device": "auto",
            "max_tokens": 50,
            "temperature": 0.1,
            "trust_remote_code": True,
            "use_fast_tokenizer": False
        },
        "classification_config": {
            "max_content_chars": 2000,
            "max_pages_to_extract": 5,
            "confidence_threshold": 60,
            "fallback_enabled": True
        },
        "prompts": {
            "classification_prompt": "<s>[INST] You are a financial document classifier. Your task is to determine if a document is an annual report or financial statement.\n\nDocument content (first 2000 characters):\n{content}\n\nBased on the content above, classify this document. Respond with ONLY one of the following:\n- \"ANNUAL_REPORT\" - if this is an annual report, financial statement, or similar comprehensive financial document\n- \"NOT_ANNUAL_REPORT\" - if this is not an annual report (e.g., quarterly report, presentation, press release, etc.)\n\nConsider these indicators for ANNUAL_REPORT:\n- Contains comprehensive financial statements\n- Mentions \"annual report\", \"financial statements\", \"consolidated statements\"\n- Contains balance sheet, income statement, cash flow statement\n- Has auditor's report or independent auditor section\n- Mentions \"for the year ended\" or similar annual period language\n- Contains comprehensive financial data and metrics\n\nConsider these indicators for NOT_ANNUAL_REPORT:\n- Quarterly or interim reports\n- Investor presentations\n- Press releases\n- Sustainability reports\n- Proxy statements\n- Fact sheets or brochures\n\nClassification: [/INST]",
            "confidence_prompt": "<s>[INST] You are a financial document classifier. Rate your confidence (0-100) in classifying the following document as an annual report.\n\nDocument content (first 2000 characters):\n{content}\n\nRate your confidence from 0-100 where:\n- 0-30: Low confidence, document is unclear or ambiguous\n- 31-70: Medium confidence, some indicators present but not definitive\n- 71-100: High confidence, clear indicators of annual report or financial statement\n\nRespond with ONLY the number (0-100): [/INST]"
        },
        "fallback_indicators": {
            "positive": [
                "annual report",
                "annual report and accounts",
                "annual review",
                "form 10-k",
                "consolidated financial statements",
                "financial statements",
                "statement of financial position",
                "balance sheet",
                "income statement",
                "statement of comprehensive income",
                "statement of cash flows",
                "cash flow statement",
                "independent auditor",
                "auditor's report",
                "for the year ended"
            ],
            "negative": [
                "interim",
                "quarter",
                "q1",
                "q2",
                "q3",
                "q4",
                "half-year",
                "half year",
                "trading update",
                "presentation",
                "investor presentation",
                "press release",
                "pillar 3",
                "sustainability report",
                "csr report",
                "proxy statement",
                "circular",
                "md&a",
                "factbook"
            ]
        }
    }
    
    with open(config_path, 'w') as f:
        json.dump(sample_config, f, indent=4)
    
    print(f"✓ Created sample configuration at {config_path}")

def test_classifier():
    """Test the classifier with a sample document."""
    print("\nTesting classifier...")
    
    try:
        from ai_classifier import classify_document, get_classifier
        
        # Test classifier initialization
        classifier = get_classifier()
        print(f"✓ Classifier initialized: {classifier.model_name}")
        
        # Check if we have any test documents
        data_dir = Path("data/reports")
        if data_dir.exists():
            pdf_files = list(data_dir.rglob("*.pdf"))
            if pdf_files:
                test_pdf = str(pdf_files[0])
                print(f"Testing with: {test_pdf}")
                
                result = classify_document(test_pdf)
                print(f"✓ Classification result: {result['is_annual_report']} (confidence: {result['confidence']}%)")
                print(f"  Method: {result.get('method', 'unknown')}")
                return True
            else:
                print("No PDF files found for testing. Please add some PDF files to data/reports/")
        else:
            print("Data directory not found. Please create data/reports/ and add some PDF files for testing.")
        
        return False
        
    except Exception as e:
        print(f"✗ Classifier test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("AI Classifier Setup")
    print("=" * 50)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check model availability
    model_ok = check_model_availability()
    
    # Create sample config
    create_sample_config()
    
    # Test classifier
    if deps_ok:
        test_ok = test_classifier()
    else:
        test_ok = False
    
    print("\n" + "=" * 50)
    print("Setup Summary:")
    print(f"Dependencies: {'✓' if deps_ok else '✗'}")
    print(f"Model: {'✓' if model_ok else '✗'}")
    print(f"Classifier Test: {'✓' if test_ok else '✗'}")
    
    if deps_ok and model_ok and test_ok:
        print("\n🎉 AI classifier is ready to use!")
        print("\nYou can now:")
        print("1. Use the classifier in your code: from ai_classifier import classify_document")
        print("2. Test with: python test_ai_classifier.py")
        print("3. Use the API endpoints: /api/ai/classify, /api/ai/classify_batch")
    else:
        print("\n⚠️  Some issues need to be resolved before using the AI classifier.")
        print("Please check the messages above and resolve any issues.")

if __name__ == "__main__":
    main()