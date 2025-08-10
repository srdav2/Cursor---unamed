import unittest
import os
import logging
from ai_classifier import AIClassifier

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestDocumentValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.classifier = AIClassifier()
        cls.test_dir = os.path.join(os.path.dirname(__file__), "..", "FOR TESTING")
        
        cls.annual_reports = [
            "anz_FY2024_Annual_Report.pdf",
            "jpm_FY2023_Annual_Report.pdf",
            "wbc_FY2023_Annual_Report.pdf",
        ]
        
        cls.non_annual_reports = {
            "ms_FY2025_Annual_Report.pdf": "Proxy Statement",
            "barc_FY2023_Annual_Report.pdf": "Proxy Statement",
            "boc_FY2025_Annual_Report.pdf": "Interim Report",
            "san_FY2017_Annual_Report.pdf": "Remuneration Report",
        }

    def test_annual_reports_are_accepted(self):
        for pdf_name in self.annual_reports:
            with self.subTest(pdf=pdf_name):
                pdf_path = os.path.join(self.test_dir, pdf_name)
                result = self.classifier.validate_document(pdf_path)
                
                logger.info(f"Testing {pdf_name}: Expected to PASS.")
                self.assertTrue(result['is_accepted'], f"{pdf_name} should be accepted.")
                self.assertEqual(result['document_type'], 'Annual Report')
                self.assertIsNone(result['stage_failed'], f"{pdf_name} should not fail at any stage.")

    def test_non_annual_reports_are_rejected(self):
        for pdf_name, expected_type in self.non_annual_reports.items():
            with self.subTest(pdf=pdf_name):
                pdf_path = os.path.join(self.test_dir, pdf_name)
                result = self.classifier.validate_document(pdf_path)
                
                logger.info(f"Testing {pdf_name}: Expected to FAIL at triage.")
                self.assertFalse(result['is_accepted'], f"{pdf_name} should be rejected.")
                self.assertEqual(result['document_type'], expected_type, f"Document type for {pdf_name} should be '{expected_type}'.")
                self.assertEqual(result['stage_failed'], 'triage', f"{pdf_name} should be rejected at the triage stage.")

if __name__ == '__main__':
    unittest.main(verbosity=2)