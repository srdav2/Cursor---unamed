import pdfplumber
import os

PDF_PATH = "data/reports/jpm/jpm_FY2023_Annual_Report.pdf"
OUTPUT_PATH = "backend/jpm_toc_analysis.txt"
PAGES_TO_EXTRACT = 20

def extract_text():
    """Extracts the first N pages of a PDF to a text file for analysis."""
    if not os.path.exists(PDF_PATH):
        print(f"Error: PDF file not found at {PDF_PATH}")
        return

    text_content = []
    try:
        with pdfplumber.open(PDF_PATH) as pdf:
            for i, page in enumerate(pdf.pages[:PAGES_TO_EXTRACT]):
                text = page.extract_text(x_tolerance=1, y_tolerance=1) or ""
                text_content.append(f"--- PAGE {i+1} ---\n{text}\n")
        
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write("".join(text_content))
        
        print(f"Successfully extracted {PAGES_TO_EXTRACT} pages to {OUTPUT_PATH} for ToC analysis.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    extract_text()

