import logging
import os
import pdfplumber
import torch
from transformers import pipeline
from typing import Dict, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIClassifier:
    def __init__(self):
        device = 0 if torch.cuda.is_available() else -1
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=device
        )

    def _extract_text_from_pages(self, pdf_path: str, start_page: int, end_page: int) -> str:
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                num_pages = len(pdf.pages)
                for i in range(start_page, min(end_page, num_pages)):
                    page_text = pdf.pages[i].extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
        return text

    def is_document_type_plausible(self, pdf_path: str) -> Tuple[str, float]:
        logger.info(f"Stage 1: Performing fast triage on {os.path.basename(pdf_path)}...")
        initial_text = self._extract_text_from_pages(pdf_path, 0, 20)
        if not initial_text.strip():
            return "Other", 0.0

        candidate_labels = ["Annual Report", "Proxy Statement", "Remuneration Report", "Interim Report", "Other"]
        result = self.classifier(initial_text, candidate_labels, multi_label=False)
        
        doc_type = result['labels'][0]
        confidence = result['scores'][0]
        
        logger.info(f"Stage 1 Result for {os.path.basename(pdf_path)}: Classified as '{doc_type}' with confidence {confidence:.2f}")
        return doc_type, confidence

    def perform_detailed_audit(self, pdf_path: str) -> Dict[str, bool]:
        logger.info(f"Stage 2: Performing deep audit on {os.path.basename(pdf_path)}...")
        audit_results = {
            "has_income_statement": False,
            "has_balance_sheet": False,
            "has_cash_flow_statement": False,
        }
        
        candidate_labels_map = {
            "Income Statement": "has_income_statement",
            "Balance Sheet": "has_balance_sheet",
            "Statement of Cash Flows": "has_cash_flow_statement",
        }
        candidate_labels = list(candidate_labels_map.keys())
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if not page_text or len(page_text) < 50:
                        continue

                    if all(audit_results.values()):
                        logger.info("Stage 2: All required statements found. Ending audit early.")
                        break

                    result = self.classifier(page_text, candidate_labels, multi_label=True)
                    
                    for label, score in zip(result['labels'], result['scores']):
                        audit_key = candidate_labels_map[label]
                        if not audit_results[audit_key] and score > 0.95:
                            audit_results[audit_key] = True
                            logger.info(f"Found '{label}' on page {i+1} with score {score:.2f}")

        except Exception as e:
            logger.error(f"Error during deep audit for {pdf_path}: {e}")

        logger.info(f"Stage 2 Audit Results: {audit_results}")
        return audit_results

    def validate_document(self, pdf_path: str) -> Dict:
        doc_type, confidence = self.is_document_type_plausible(pdf_path)

        if doc_type != "Annual Report":
            return {
                "document_type": doc_type,
                "confidence_score": confidence * 10,
                "is_accepted": False,
                "stage_failed": "triage",
                "audit": {}
            }

        audit = self.perform_detailed_audit(pdf_path)
        is_accepted = all(audit.values())
        
        return {
            "document_type": "Annual Report",
            "confidence_score": confidence * 10,
            "is_accepted": is_accepted,
            "stage_failed": None if is_accepted else "deep_audit",
            "audit": audit
        }