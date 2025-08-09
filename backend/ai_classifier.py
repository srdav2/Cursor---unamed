import json
import logging
import os
import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

import requests
import pdfplumber

# Try to import AI dependencies
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    AI_DEPENDENCIES_AVAILABLE = True
except ImportError:
    AI_DEPENDENCIES_AVAILABLE = False
    logging.warning("AI dependencies not available. Install torch and transformers for AI classification.")

logger = logging.getLogger(__name__)

class AnnualReportClassifier:
    """
    AI-powered classifier for determining if a document is an annual report or financial statement.
    Uses a local 8B Llama model for classification.
    """
    
    def __init__(self, config_path: Optional[str] = None, model_name: str = "meta-llama/Llama-2-7b-chat-hf", device: str = "auto"):
        """
        Initialize the classifier with a local Llama model.
        
        Args:
            config_path: Path to configuration file
            model_name: HuggingFace model name or local path
            device: Device to run model on ("auto", "cpu", "cuda", "mps")
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Override config with parameters if provided
        if model_name != "meta-llama/Llama-2-7b-chat-hf":
            self.config["model_config"]["model_name"] = model_name
        if device != "auto":
            self.config["model_config"]["device"] = device
            
        self.model_name = self.config["model_config"]["model_name"]
        
        # Handle device detection
        if self.config["model_config"]["device"] == "auto":
            if AI_DEPENDENCIES_AVAILABLE and torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"
        else:
            self.device = self.config["model_config"]["device"]
        
        # Initialize model and tokenizer
        self.tokenizer = None
        self.model = None
        
        if AI_DEPENDENCIES_AVAILABLE:
            self._load_model()
        else:
            logger.warning("AI dependencies not available. Using fallback classification.")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "ai_config.json")
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded AI configuration from {config_path}")
                return config
            else:
                logger.warning(f"Config file not found at {config_path}, using defaults")
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}, using defaults")
        
        # Default configuration
        return {
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
                    "annual report", "annual report and accounts", "annual review", "form 10-k",
                    "consolidated financial statements", "financial statements",
                    "statement of financial position", "balance sheet",
                    "income statement", "statement of comprehensive income",
                    "statement of cash flows", "cash flow statement",
                    "independent auditor", "auditor's report", "for the year ended",
                ],
                "negative": [
                    "interim", "quarter", "q1", "q2", "q3", "q4", "half-year", "half year",
                    "trading update", "presentation", "investor presentation", "press release", "pillar 3",
                    "sustainability report", "csr report", "proxy statement", "circular", "md&a", "factbook"
                ]
            }
        }
    
    def _load_model(self):
        """Load the Llama model and tokenizer."""
        if not AI_DEPENDENCIES_AVAILABLE:
            logger.warning("AI dependencies not available. Skipping model loading.")
            return
            
        try:
            logger.info(f"Loading model {self.model_name} on device {self.device}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=self.config["model_config"]["trust_remote_code"],
                use_fast=self.config["model_config"]["use_fast_tokenizer"]
            )
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True,
                trust_remote_code=self.config["model_config"]["trust_remote_code"]
            )
            
            if self.device != "cuda":
                self.model = self.model.to(self.device)
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
            self.tokenizer = None
    
    def _extract_text_from_pdf(self, pdf_path: str, max_chars: Optional[int] = None) -> str:
        """
        Extract text from PDF for classification.
        
        Args:
            pdf_path: Path to PDF file
            max_chars: Maximum characters to extract
            
        Returns:
            Extracted text
        """
        if max_chars is None:
            max_chars = self.config["classification_config"]["max_content_chars"]
            
        max_pages = self.config["classification_config"]["max_pages_to_extract"]
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                texts = []
                total_chars = 0
                
                # Extract from first few pages
                for page in pdf.pages[:max_pages]:
                    if total_chars >= max_chars:
                        break
                    
                    text = page.extract_text() or ""
                    if text:
                        texts.append(text)
                        total_chars += len(text)
                
                combined_text = "\n".join(texts)
                return combined_text[:max_chars]
                
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            return ""
    
    def _generate_response(self, prompt: str) -> str:
        """
        Generate response from the model.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Model response
        """
        if not AI_DEPENDENCIES_AVAILABLE or self.model is None:
            return ""
            
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt")
            if self.device != "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.config["model_config"]["max_tokens"],
                    temperature=self.config["model_config"]["temperature"],
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract the response part after the instruction
            if "[/INST]" in response:
                response = response.split("[/INST]")[-1].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return ""
    
    def _fallback_classification(self, content: str) -> Dict[str, Any]:
        """
        Fallback classification using rule-based approach when AI is not available.
        
        Args:
            content: Document content
            
        Returns:
            Classification result
        """
        content_lower = content.lower()
        
        # Get indicators from config
        positive_indicators = self.config["fallback_indicators"]["positive"]
        negative_indicators = self.config["fallback_indicators"]["negative"]
        
        # Count indicators
        positive_count = sum(1 for indicator in positive_indicators if indicator in content_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in content_lower)
        
        # Calculate confidence based on indicator balance
        total_indicators = positive_count + negative_count
        if total_indicators == 0:
            confidence = 30  # Low confidence if no clear indicators
        else:
            confidence = int((positive_count / total_indicators) * 100)
        
        is_annual_report = positive_count > negative_count and confidence >= 50
        
        return {
            "is_annual_report": is_annual_report,
            "confidence": confidence,
            "reasoning": f"Fallback classification: {positive_count} positive, {negative_count} negative indicators",
            "method": "fallback"
        }
    
    def classify_document(self, pdf_path: str) -> Dict[str, Any]:
        """
        Classify a document as annual report or not.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with classification results
        """
        if not os.path.exists(pdf_path):
            return {
                "is_annual_report": False,
                "confidence": 0,
                "reasoning": "File not found",
                "error": "File not found",
                "method": "error"
            }
        
        # Extract text from PDF
        content = self._extract_text_from_pdf(pdf_path)
        if not content:
            return {
                "is_annual_report": False,
                "confidence": 0,
                "reasoning": "No text extracted",
                "error": "No text extracted",
                "method": "error"
            }
        
        # Try AI classification first
        if AI_DEPENDENCIES_AVAILABLE and self.model is not None:
            try:
                # Classify the document
                classification_prompt = self.config["prompts"]["classification_prompt"].format(content=content[:2000])
                classification_response = self._generate_response(classification_prompt)
                
                # Determine classification
                is_annual_report = "ANNUAL_REPORT" in classification_response.upper()
                
                # Get confidence score
                confidence_prompt = self.config["prompts"]["confidence_prompt"].format(content=content[:2000])
                confidence_response = self._generate_response(confidence_prompt)
                
                # Extract confidence number
                confidence = 50  # Default confidence
                try:
                    confidence_match = re.search(r'\b(\d{1,3})\b', confidence_response)
                    if confidence_match:
                        confidence = int(confidence_match.group(1))
                        confidence = max(0, min(100, confidence))  # Clamp to 0-100
                except:
                    pass
                
                return {
                    "is_annual_report": is_annual_report,
                    "confidence": confidence,
                    "reasoning": classification_response,
                    "content_preview": content[:500] + "..." if len(content) > 500 else content,
                    "method": "ai"
                }
                
            except Exception as e:
                logger.warning(f"AI classification failed: {e}. Using fallback.")
        
        # Fallback to rule-based classification
        return self._fallback_classification(content)
    
    def classify_batch(self, pdf_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Classify multiple documents.
        
        Args:
            pdf_paths: List of PDF file paths
            
        Returns:
            List of classification results
        """
        results = []
        for pdf_path in pdf_paths:
            result = self.classify_document(pdf_path)
            result["pdf_path"] = pdf_path
            results.append(result)
        return results

# Global classifier instance
_classifier_instance = None

def get_classifier() -> AnnualReportClassifier:
    """Get or create the global classifier instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = AnnualReportClassifier()
    return _classifier_instance

def classify_document(pdf_path: str) -> Dict[str, Any]:
    """
    Convenience function to classify a single document.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Classification results
    """
    classifier = get_classifier()
    return classifier.classify_document(pdf_path)

def classify_batch(pdf_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Convenience function to classify multiple documents.
    
    Args:
        pdf_paths: List of PDF file paths
        
    Returns:
        List of classification results
    """
    classifier = get_classifier()
    return classifier.classify_batch(pdf_paths)