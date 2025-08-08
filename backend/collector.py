import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from scraper import ensure_directory, extract_year_candidates, BANK_REGISTRY
import pdfplumber
import shutil
import time
import ollama


def triage_document_type_with_ollama(pdf_path: str, timeout: int = 30) -> Optional[Dict[str, any]]:
    """
    Use local Ollama Llama3.1 to classify the document type from the first few pages.
    Returns a dict with 'document_type' and 'confidence_score' (0-10) or None on failure.
    """
    try:
        client = ollama.Client(timeout=timeout)
        # Check if model is available, to provide a better error message.
        try:
            client.show('phi3:mini')
        except ollama.ResponseError as e:
            if e.status_code == 404:
                logger.error("Ollama model 'phi3:mini' not found. Please run `ollama pull llama3.1:8b`")
                return None
            raise

        text = _read_pdf_text_head(pdf_path, max_pages=5)
        if not text.strip():
            return None

        prompt = f"""
Analyze the following text from the first few pages of a financial document.
Based on the content, classify the document into ONE of the following categories:
- Annual Report
- Interim Report (e.g., quarterly, half-year)
- Investor Presentation
- Press Release
- Other (e.g., sustainability report, proxy statement, circular)

Also, provide a confidence score from 0 to 10 for your classification.
Respond ONLY with a valid JSON object in the format:
{{"document_type": "...", "confidence_score": ...}}

Document Text:
---
{text[:8000]}
---
"""
        response = client.generate(
            model='phi3:mini',
            prompt=prompt,
            format='json',
            options={'temperature': 0.1}
        )
        
        response_text = response.get('response', '{}').strip()
        # The model sometimes returns the JSON wrapped in markdown ```json ... ```
        response_text = re.sub(r'^```json\s*|\s*```$', '', response_text)
        
        data = json.loads(response_text)
        
        doc_type = data.get("document_type")
        score = data.get("confidence_score")

        if isinstance(doc_type, str) and isinstance(score, (int, float)):
            return {"document_type": doc_type, "confidence_score": float(score)}
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response from Ollama: {e}")
    except ollama.ResponseError as e:
        logger.error(f"Ollama API error: {e.status_code} - {e.error}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while classifying with Ollama: {e}")
        
    return None


def verify_financial_statements_with_ollama(pdf_path: str, timeout: int = 45) -> Dict[str, bool]:
    """
    Scans the first 25 pages of a PDF to verify the presence of key financial statements.
    """
    results = {
        "has_income_statement": False,
        "has_balance_sheet": False,
        "has_cash_flow_statement": False,
    }
    try:
        text = _read_pdf_text_head(pdf_path, max_pages=25)
        if not text.strip():
            return results

        prompt = f"""
As an auditor, your task is to verify the presence of the three main financial statements in this document's text, which is from the first ~25 pages of a financial report.
Read the text and determine if it explicitly contains:
1.  An Income Statement (might be called 'Consolidated Statement of Income', 'Statement of Operations', or 'Profit and Loss').
2.  A Balance Sheet (might be called 'Consolidated Statement of Financial Position').
3.  A Statement of Cash Flows (might be called 'Consolidated Statement of Cash Flows').

You MUST respond ONLY with a valid JSON object with boolean flags. Example:
{{"has_income_statement": true, "has_balance_sheet": true, "has_cash_flow_statement": false}}

Document Text:
---
{text[:12000]}
---
"""
        client = ollama.Client(timeout=timeout)
        response = client.generate(
            model='phi3:mini',
            prompt=prompt,
            format='json',
            options={'temperature': 0.0}
        )
        response_text = response.get('response', '{}').strip()
        response_text = re.sub(r'^```json\s*|\s*```$', '', response_text)
        data = json.loads(response_text)

        results["has_income_statement"] = bool(data.get("has_income_statement"))
        results["has_balance_sheet"] = bool(data.get("has_balance_sheet"))
        results["has_cash_flow_statement"] = bool(data.get("has_cash_flow_statement"))

    except Exception as e:
        logger.error(f"Ollama statement verification failed: {e}")
    
    return results


def find_annual_report_page_with_ollama(html_content: str, url: str) -> float:
    """
    Use Ollama to determine if a webpage is a good candidate for finding annual reports.
    Returns a score from 0.0 to 1.0.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Try to find the main content area to reduce noise
        main_content = soup.find('main') or soup.find('article') or soup.find('div', id='main') or soup
        text = main_content.get_text(separator='\n', strip=True)

        if not text.strip():
            return 0.0

        prompt = f"""
As a financial analyst, your task is to evaluate if a webpage is the primary page for a bank's annual financial reports.
Analyze the text content from the URL: {url}
Based on the text, which includes headings, link text, and paragraphs, does this page seem dedicated to listing annual reports, or is it a general investor page, news page, or something else?
A good page will have phrases like "Annual Report", "Financial Statements", and a list of years. A bad page will be about news, stock price, or general governance.

Respond with a single float number from 0.0 (not a report page) to 1.0 (definitely the main report page).

Webpage Text (first 8000 chars):
---
{text[:8000]}
---
"""
        client = ollama.Client(timeout=30)
        response = client.generate(
            model='phi3:mini',
            prompt=prompt,
            # No JSON format, expect a simple float string
        )
        response_text = response.get('response', '0.0').strip()
        # Extract the first valid float from the response
        match = re.search(r'[-+]?\d*\.\d+|\d+', response_text)
        if match:
            return float(match.group())
    except Exception as e:
        logger.error(f"Ollama page analysis failed for {url}: {e}")
    return 0.0



logger = logging.getLogger(__name__)
def _year_bounds() -> Tuple[int, int]:
    current_year = datetime.utcnow().year
    return 2015, current_year + 1



# Map bank codes to likely investor relations pages that list annual reports.
# This list can be expanded over time.
# Load bank sources from JSON if available; fallback to built-in defaults
DEFAULT_BANK_SOURCES: Dict[str, List[str]] = {
    # Australia
    "cba": [
        "https://www.commbank.com.au/about-us/investors/financials/annual-reports.html",
        "https://www.commbank.com.au/about-us/investors/financials.html",
    ],
    "nab": [
        "https://www.nab.com.au/about-us/company/who-we-are/annual-report",
        "https://www.nab.com.au/about-us/company/investor-centre/annual-reports",
    ],
    "wbc": [
        "https://www.westpac.com.au/about-westpac/investor-centre/financial-information/annual-reports/",
    ],
    "anz": [
        "https://www.anz.com/shareholder/centre/reporting/annual-reports/",
    ],
    "mqg": [
        "https://www.macquarie.com/au/en/investors/reports/annual.html",
    ],

    # Canada (examples; may need refinement)
    "rbc": ["https://www.rbc.com/investor-relations/annual-report.html"],
    "td": ["https://www.td.com/ca/en/about-td/investor-relations/annual-reports"],
    "bns": ["https://www.scotiabank.com/ca/en/about/investors-shareholders/financial-results.html"],
    "bmo": ["https://www.bmo.com/main/about-bmo/investor-relations/financial-information/annual-reports/"],
    "cm": ["https://www.cibc.com/en/about-cibc/investor-relations/financial-information/annual-reports.html"],
    "nbc": ["https://www.nbc.ca/en/about-us/investors/financial-information/annual-reports.html"],

    # United States
    "jpm": ["https://www.jpmorganchase.com/ir/annual-reports"],
    "bac": ["https://investor.bankofamerica.com/financials/annual-reports/default.aspx"],
    "wfc": ["https://www.wellsfargo.com/about/investor-relations/annual-reports/"],
    "c": ["https://www.citigroup.com/global/investors/annual-reports"],
    "gs": ["https://www.goldmansachs.com/investor-relations/financials/annual-reports/"],
    "ms": ["https://www.morganstanley.com/about-us-ir/annual-reports"],

    # United Kingdom
    "hsbc": ["https://www.hsbc.com/investors/results-and-announcements"],
    "barc": ["https://home.barclays/investors/investor-archives/annual-reports/"],
    "lloy": ["https://www.lloydsbankinggroup.com/investors/financial-performance/annual-report/"],
    "nwg": ["https://www.natwestgroup.com/investors/financial-results/annual-reports.html"],
    "stan": ["https://www.sc.com/en/investors/financial-results/"],

    # Eurozone
    "bnpp": ["https://invest.bnpparibas/en/financial-information/financial-reports"],
    "aca": ["https://www.credit-agricole.com/en/finance/financial-publications"],
    "san": ["https://www.santander.com/en/shareholders-and-investors/financial-and-economic-information"],
    "ing": ["https://www.ing.com/Investor-relations/Financial-information/Annual-reports.htm"],
    "dbk": ["https://investor-relations.db.com/en/financials-reports/reports/"],
    "isp": ["https://group.intesasanpaolo.com/en/investor-relations/financial-reports"],

    # Switzerland
    "ubs": ["https://www.ubs.com/global/en/investor-relations/financial-information/annual-reporting.html"],

    # Japan
    "mufg": ["https://www.mufg.jp/english/ir/library/annualreport/"],
    "smfg": ["https://www.smfg.co.jp/english/investor/library/annual/"],
    "mizuho": ["https://www.mizuho-fg.com/investors/financial/annual/"],

    # China (English IR pages)
    "icbc": ["https://www.icbc.com.cn/ICBC/Investor%20Relations/Financials/"],
    "ccb": ["http://www.ccb.com/en/investor/financial_report/"],
    "abc": ["https://www.abchina.com/en/AboutABC/Investor-Relations/Financial-Statements/"],
    "boc": ["https://www.boc.cn/en/investor/ir3/"],

    # Singapore
    "dbs": ["https://www.dbs.com/investors/financials/annual-report"],
    "ocbc": ["https://www.ocbc.com/investors/annual-reports"],
    "uob": ["https://www.uobgroup.com/investor-relations/financial/annual-reports.page"],
}

def load_bank_sources() -> Dict[str, List[str]]:
    path = os.path.join(os.path.dirname(__file__), 'bank_sources.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return {k.lower(): v for k, v in data.items() if isinstance(v, list)}
    except Exception:
        pass
    return DEFAULT_BANK_SOURCES


def http_get(url: str, timeout: int = 30) -> requests.Response:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response


def extract_pdf_links_from_html(html: str, base_url: str) -> List[Tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    out: List[Tuple[str, str]] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        abs_url = urljoin(base_url, href)
        if abs_url.lower().endswith(".pdf"):
            text = a.get_text(" ", strip=True) or ""
            out.append((abs_url, text))
    return out


def pre_download_filter(url: str, text: str) -> bool:
    """
    Apply strict heuristics to link text to avoid downloading obvious non-annual reports.
    Returns True if the link is a plausible candidate, False otherwise.
    """
    lower_text = text.lower()
    lower_url = url.lower()

    # Strong positive signals
    positive_keywords = ["annual report", "annual financial report", "form 10-k", "annual review"]
    if any(keyword in lower_text for keyword in positive_keywords):
        return True
    if any(keyword.replace(' ', '') in lower_url for keyword in positive_keywords):
        return True

    # Strong negative signals that immediately disqualify
    negative_keywords = [
        "interim", "quarter", "q1", "q2", "q3", "q4", "half-year", "half year",
        "trading update", "presentation", "investor day", "webcast", "transcript",
        "press release", "news", "pillar 3", "sustainability", "esg", "csr",
        "proxy statement", "circular", "notice of meeting", "agm",
        "fact sheet", "factbook", "results announcement"
    ]
    if any(keyword in lower_text for keyword in negative_keywords):
        return False
    if any(keyword.replace(' ', '') in lower_url for keyword in negative_keywords):
        return False

    # If no strong signals, be permissive but this can be tightened
    return False # Default to false to be strict


def discover_annual_reports(bank: str) -> List[Tuple[int, str, str]]:
    """
    Discover candidate (year, pdf_url, label) tuples for a bank from configured sources.
    Uses Ollama to score and prioritize promising pages.
    """
    sources_map = load_bank_sources()
    initial_sources = sources_map.get(bank.lower(), [])
    results: List[Tuple[int, str, str]] = []
    
    min_year, max_year = _year_bounds()
    
    # Use Ollama to find the best source pages from the initial list
    scored_sources = []
    for src_url in initial_sources:
        try:
            r = http_get(src_url)
            score = find_annual_report_page_with_ollama(r.text, src_url)
            if score > 0.3: # Threshold for considering a page
                scored_sources.append((score, src_url, r.text))
        except Exception as exc:
            logger.warning("Could not analyze source %s: %s", src_url, exc)
    
    # Sort by score descending, so we check the best pages first
    scored_sources.sort(key=lambda x: x[0], reverse=True)

    # Limit to top N sources to avoid excessive scraping
    for score, src_url, src_html in scored_sources[:3]:
        logger.info(f"Processing source '{src_url}' (Ollama score: {score:.2f})")
        try:
            soup = BeautifulSoup(src_html, "html.parser")
            
            # 1. Direct PDF links from the high-quality source page
            pdf_links = extract_pdf_links_from_html(src_html, src_url)
            for url, label in pdf_links:
                if pre_download_filter(url, label):
                    years = extract_year_candidates(label) or extract_year_candidates(url)
                    if years:
                        year = max(y for y in years if min_year <= y <= max_year)
                        if year:
                            results.append((year, url, label))

            # 2. Follow promising sub-pages (depth-1)
            candidate_pages: List[str] = []
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if not href or href.startswith('#') or href.lower().endswith(".pdf"):
                    continue
                
                label = (a.get_text(" ", strip=True) or "").lower()
                # Use pre-download filter keywords to find promising sub-pages
                if any(kw in label for kw in ["annual report", "financial statement", "archive", "all reports"]):
                    candidate_pages.append(urljoin(src_url, href))

            for page_url in list(set(candidate_pages))[:5]:  # Safety cap
                try:
                    pr = http_get(page_url)
                    sub_pdfs = extract_pdf_links_from_html(pr.text, page_url)
                    for url, label in sub_pdfs:
                        if pre_download_filter(url, label):
                            years = extract_year_candidates(label) or extract_year_candidates(url)
                            if years:
                                year = max(y for y in years if min_year <= y <= max_year)
                                if year:
                                    results.append((year, url, label))
                except Exception as exc:
                    logger.debug("Skip candidate page %s: %s", page_url, exc)
        except Exception as exc:
            logger.warning("Failed to parse %s: %s", src_url, exc)

    # Deduplicate by (year, url)
    dedup: Dict[Tuple[int, str], Tuple[int, str, str]] = {}
    for y, u, l in results:
        dedup[(y, u)] = (y, u, l)
    return sorted(dedup.values(), key=lambda t: t[0], reverse=True)


def choose_latest_n_years(candidates: List[Tuple[int, str, str]], n: int = 6) -> List[Tuple[int, str, str]]:
    # Filter to a sensible FY window (e.g., 2015..current_year+1)
    min_year, max_year = _year_bounds()
    filtered = [(y, u, l) for (y, u, l) in candidates if min_year <= y <= max_year]
    # Sort by year desc and pick top distinct years
    seen: set[int] = set()
    chosen: List[Tuple[int, str, str]] = []
    for year, url, label in sorted(filtered, key=lambda t: t[0], reverse=True):
        if year in seen:
            continue
        seen.add(year)
        chosen.append((year, url, label))
        if len(chosen) >= n:
            break
    return chosen


def download_file(url: str, dest_path: str) -> str:
    ensure_directory(os.path.dirname(dest_path))
    with requests.get(url, stream=True) as r:  # type: ignore[call-arg]
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return dest_path


def _read_pdf_text_head(pdf_path: str, max_pages: int = 10) -> str:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            texts = []
            for i, page in enumerate(pdf.pages[:max_pages]):
                t = page.extract_text() or ""
                texts.append(t)
            return "\n".join(texts)
    except Exception:
        return ""


def compute_financial_report_score(pdf_path: str, bank: Optional[str], year: Optional[int]) -> int:
    """Heuristic scoring; higher is better for annual financial statements."""
    text = _read_pdf_text_head(pdf_path, max_pages=8).lower()
    if not text:
        return 0

    score = 0
    # Positive signals
    positives = [
        "annual report", "annual report and accounts", "annual review", "form 10-k",
        "consolidated financial statements", "financial statements",
        "statement of financial position", "balance sheet",
        "income statement", "statement of comprehensive income",
        "statement of cash flows", "cash flow statement",
        "independent auditor", "auditor's report", "for the year ended",
    ]
    score += sum(2 for k in positives if k in text)

    # Bank name/token
    if bank and bank.lower() in BANK_REGISTRY:
        name = (BANK_REGISTRY[bank.lower()].get("name") or "").lower()
        code = bank.lower()
        if name:
            first_token = name.split(" ")[0]
            if first_token in text:
                score += 1
            if name in text:
                score += 1
        if code in text:
            score += 1

    # Year hints
    if year and (str(year) in text or f"fy{str(year)[-2:]}" in text or f"{year} annual" in text):
        score += 2

    # SEC hints for US
    if "securities and exchange commission" in text or "washington, d.c." in text:
        score += 2

    # Negative signals (interim/quarterly/presentation)
    negatives = [
        "interim", "quarter", "q1", "q2", "q3", "q4", "half-year", "half year",
        "trading update", "presentation", "investor presentation", "press release", "pillar 3",
        "sustainability report", "csr report", "proxy statement", "circular", "md&a", "factbook"
    ]
    score -= sum(2 for k in negatives if k in text)

    return max(score, 0)


def is_likely_financial_report(pdf_path: str, bank: Optional[str], year: Optional[int]) -> Tuple[bool, Optional[Dict[str, any]]]:
    """
    Performs a 2-step validation:
    1. Triage the document type (e.g., Annual Report, Proxy Statement).
    2. If it looks like an Annual Report, verify it contains the key financial statements.
    """
    # Step 1: Triage the document type
    triage_details = triage_document_type_with_ollama(pdf_path)
    if not triage_details:
        # Fallback to old heuristic if Ollama fails for triage
        score = compute_financial_report_score(pdf_path, bank, year)
        is_accepted = score >= 5 # Use a slightly higher threshold for heuristic
        fallback_details = {
            "document_type": "Annual Report" if is_accepted else "Other",
            "confidence_score": min(score, 10),
            "source": "heuristic",
            "audit": {"error": "Triage failed, used heuristic fallback."}
        }
        return is_accepted, fallback_details

    doc_type = triage_details.get("document_type", "Other")
    score = triage_details.get("confidence_score", 0)

    # If triage does not identify it as an Annual Report, reject it immediately.
    if doc_type != "Annual Report" or score < 7:
        triage_details["audit"] = {"message": f"Rejected at triage stage due to type '{doc_type}' and score {score}."}
        return False, triage_details

    # Step 2: Verify the presence of core financial statements
    audit_results = verify_financial_statements_with_ollama(pdf_path)
    triage_details["audit"] = audit_results
    
    # A true annual report must contain all three statements.
    is_fully_audited = all(audit_results.values())
    
    if not is_fully_audited:
        missing = [k for k, v in audit_results.items() if not v]
        logger.info(f"Rejected '{pdf_path}' because it was missing: {', '.join(missing)}")

    return is_fully_audited, triage_details


def download_and_validate(url: str, dest_path: str, bank: Optional[str], year: Optional[int]) -> Optional[Dict[str, any]]:
    """
    Downloads a file, validates it, and if accepted, returns its path and classification details.
    """
    tmp_path = dest_path + ".tmp"
    try:
        download_file(url, tmp_path)
        is_accepted, details = is_likely_financial_report(tmp_path, bank, year)
        
        if is_accepted:
            ensure_directory(os.path.dirname(dest_path))
            try:
                os.replace(tmp_path, dest_path)
            except OSError:
                shutil.copyfile(tmp_path, dest_path)
            
            # Persist classification details alongside the file
            if details:
                with open(dest_path + ".classification.json", "w", encoding="utf-8") as f:
                    json.dump(details, f)

            return {"path": dest_path, "classification": details}
        else:
            logger.info(f"Rejected document for {bank} FY{year} from {url}. Reason: {details}")
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            return None
    except Exception as e:
        logger.error(f"Failed to download/validate {url}: {e}")
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass
        return None


def build_report_path(bank: str, year: int) -> str:
    directory = os.path.join("data", "reports", bank.lower())
    ensure_directory(directory)
    filename = f"{bank.lower()}_FY{year}_Annual_Report.pdf"
    return os.path.join(directory, filename)


def update_index(index_path: str = "data/index.json") -> Dict[str, Dict[str, List[Dict[str, any]]]]:
    base_dir = os.path.join("data", "reports")
    index: Dict[str, Dict[str, List[Dict[str, any]]]] = {}
    if not os.path.exists(base_dir):
        return index
    for bank in os.listdir(base_dir):
        bank_dir = os.path.join(base_dir, bank)
        if not os.path.isdir(bank_dir):
            continue
        entries: List[Dict[str, any]] = []
        for fname in os.listdir(bank_dir):
            if not fname.lower().endswith(".pdf"):
                continue
            m = re.match(rf"{re.escape(bank)}_FY(20\d\d)_Annual_Report\.pdf$", fname, re.IGNORECASE)
            if not m:
                continue
            year = m.group(1)
            file_path = os.path.join("data", "reports", bank, fname)
            abs_path = os.path.join(base_dir, bank, fname)
            size = 0
            try:
                size = os.path.getsize(abs_path)
            except OSError:
                size = 0
            
            # Skip out-of-range years
            try:
                y_int = int(year)
                min_year, max_year = _year_bounds()
                if not (min_year <= y_int <= max_year):
                    continue
            except Exception:
                continue

            # Load classification details if they exist
            classification = None
            classification_path = abs_path + ".classification.json"
            if os.path.exists(classification_path):
                try:
                    with open(classification_path, 'r', encoding='utf-8') as f:
                        classification = json.load(f)
                except Exception:
                    pass
            
            # Fallback to heuristic score if no classification file
            if not classification:
                is_fin, details = is_likely_financial_report(abs_path, bank, int(year))
                classification = details
            else:
                 is_fin = classification.get("document_type") == "Annual Report"

            entries.append({
                "year": year,
                "path": file_path,
                "size_bytes": size,
                "abs_path": abs_path,
                "is_financial": is_fin,
                "classification": classification,
            })
        entries.sort(key=lambda e: e["year"], reverse=True)
        index[bank] = {"reports": entries}
    ensure_directory(os.path.dirname(index_path))
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    return index


def collect_bank_reports(bank: str, years: int = 6) -> Dict[str, List[Dict[str, str]]]:
    """
    Discover and download up to `years` most recent annual reports for the bank.
    Returns a structure suitable for inclusion in index.json.
    """
    bank = bank.lower()
    discovered = discover_annual_reports(bank)
    chosen = choose_latest_n_years(discovered, years)
    saved: List[Dict[str, str]] = []
    for year, url, _label in chosen:
        dest = build_report_path(bank, year)
        result = download_and_validate(url, dest, bank, year)
        if result and result.get("path"):
            saved.append({"year": str(year), "path": result["path"]})
        else:
            logger.warning("Rejected non-financial PDF for %s %s: %s", bank, year, url)
    return {"reports": saved}


def collect_all(banks: List[str], years: int = 6) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    aggregate: Dict[str, Dict[str, List[Dict[str, str]]]] = {}
    for bank in banks:
        aggregate[bank] = collect_bank_reports(bank, years)
    # refresh index file
    update_index()
    return aggregate


def collect_from_urls(bank: str, items: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    """
    Manually ingest reports from provided URLs or local file paths.
    items: [ {"year": "2024", "url": "https://.../AnnualReport.pdf" or local path } ]
    """
    bank = bank.lower()
    saved: List[Dict[str, str]] = []
    for item in items:
        year_str = str(item.get("year", "")).strip()
        url = (item.get("url") or "").strip()
        if not year_str or not url:
            continue
        try:
            year = int(year_str)
        except Exception:
            continue
        dest = build_report_path(bank, year)
        try:
            if url.lower().startswith("http://") or url.lower().startswith("https://"):
                result = download_and_validate(url, dest, bank, year)
                if not (result and result.get("path")):
                    continue
            else:
                # treat as local file path
                if os.path.exists(url):
                    ensure_directory(os.path.dirname(dest))
                    shutil.copyfile(url, dest)
                    # validate local file; delete if not a financial report
                    is_accepted, details = is_likely_financial_report(dest, bank, year)
                    if not is_accepted:
                        logger.info(f"Rejected local file {url}. Reason: {details}")
                        try:
                            os.remove(dest)
                        except OSError:
                            pass
                        continue
                    if details:
                         with open(dest + ".classification.json", "w", encoding="utf-8") as f:
                            json.dump(details, f)
                else:
                    logger.warning("Local path not found: %s", url)
                    continue
            saved.append({"year": str(year), "path": dest})
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to ingest %s %s: %s", bank, year, exc)
    update_index()
    return {"reports": saved}


def validate_library(throttle_secs: int = 0, force_revalidate: bool = False):
    """
    Generator function that yields classification progress events for streaming.
    Skips documents that have already been confirmed as Annual Reports, unless force_revalidate is True.
    """
    base_dir = os.path.join("data", "reports")
    if not os.path.exists(base_dir):
        yield {"type": "finish", "reclassified": 0, "failed": 0, "skipped": 0, "message": "No reports directory found."}
        return

    all_pdfs = []
    for bank in os.listdir(base_dir):
        bank_dir = os.path.join(base_dir, bank)
        if not os.path.isdir(bank_dir):
            continue
        for fname in os.listdir(bank_dir):
            if fname.lower().endswith(".pdf"):
                all_pdfs.append((bank, fname, os.path.join(bank_dir, fname)))
    
    total_docs = len(all_pdfs)
    yield {"type": "start", "total": total_docs, "message": f"Starting validation for {total_docs} documents..."}

    reclassified = 0
    failed = 0
    skipped = 0
    for i, (bank, fname, abs_path) in enumerate(all_pdfs):
        yield {"type": "progress", "current": i + 1, "total": total_docs, "path": fname}
        
        classification_path = abs_path + ".classification.json"
        
        # Check if already validated and confirmed, and if we are not forcing a re-validation
        if not force_revalidate and os.path.exists(classification_path):
            try:
                with open(classification_path, 'r', encoding='utf-8') as f:
                    existing_class = json.load(f)
                if existing_class.get("document_type") == "Annual Report" and (existing_class.get("confidence_score", 0) >= 7 or existing_class.get("source") == "manual_approval"):
                    is_audited = existing_class.get("audit", {}).get("has_income_statement") and existing_class.get("audit", {}).get("has_balance_sheet") and existing_class.get("audit", {}).get("has_cash_flow_statement")
                    if is_audited or existing_class.get("source") == "manual_approval":
                      skipped += 1
                      yield {"type": "result", "path": fname, "status": "skipped", "details": existing_class}
                      # Throttle even when skipping to not flood the UI
                      if throttle_secs > 0 and i < total_docs - 1:
                          time.sleep(min(float(throttle_secs) / 4.0, 0.25))
                      continue
            except Exception:
                pass # Will proceed to re-validate

        m = re.match(rf"{re.escape(bank)}_FY(\d+)_Annual_Report\.pdf$", fname, re.IGNORECASE)
        year = int(m.group(1)) if m else None

        try:
            is_accepted, details = is_likely_financial_report(abs_path, bank, year)
            if details:
                with open(classification_path, "w", encoding="utf-8") as f:
                    json.dump(details, f)
                reclassified += 1
                yield {"type": "result", "path": fname, "status": "success", "details": details}
            else:
                failed += 1
                yield {"type": "result", "path": fname, "status": "failure", "details": {"error": "Classification returned no details."}}
        except Exception as e:
            logger.error(f"Failed to re-validate {abs_path}: {e}")
            failed += 1
            yield {"type": "result", "path": fname, "status": "error", "details": {"error": str(e)}}
        
        # Throttle between requests to not overload the system
        if throttle_secs > 0 and i < total_docs - 1:
            time.sleep(throttle_secs)

    update_index()
    yield {"type": "finish", "reclassified": reclassified, "failed": failed, "skipped": skipped, "message": "Validation complete."}


def cleanup_reports() -> Dict[str, List[str]]:
    """Remove zero-byte and out-of-range year files from data/reports to fix mislabels."""
    base_dir = os.path.join("data", "reports")
    removed: List[str] = []
    if not os.path.exists(base_dir):
        return {"removed": removed}
    min_year, max_year = _year_bounds()
    for bank in os.listdir(base_dir):
        bank_dir = os.path.join(base_dir, bank)
        if not os.path.isdir(bank_dir):
            continue
        for fname in os.listdir(bank_dir):
            if not fname.lower().endswith('.pdf'):
                continue
            m = re.match(rf"{re.escape(bank)}_FY(\d+)_Annual_Report\.pdf$", fname, re.IGNORECASE)
            if not m:
                # non-conforming name; remove
                try:
                    os.remove(os.path.join(bank_dir, fname))
                    removed.append(os.path.join(bank_dir, fname))
                except OSError:
                    pass
                continue
            year = int(m.group(1))
            abs_path = os.path.join(bank_dir, fname)
            size = 0
            try:
                size = os.path.getsize(abs_path)
            except OSError:
                size = 0
            # delete zero-byte, out-of-range, and non-financial PDFs
            if size == 0 or not (min_year <= year <= max_year) or not is_likely_financial_report(abs_path, bank, year):
                try:
                    os.remove(abs_path)
                    removed.append(abs_path)
                except OSError:
                    pass
    update_index()
    return {"removed": removed}


def migrate_existing() -> Dict[str, List[str]]:
    """
    Migrate any PDFs under data/downloads/ to standardized naming if we can infer bank+year.
    Recognizes FY\d{2} (assumes 20xx) or 20\d{2} in filename; bank inferred by code substring.
    """
    moved: List[str] = []
    downloads = os.path.join('data', 'downloads')
    if not os.path.exists(downloads):
        return {"moved": moved}
    bank_codes = list(BANK_SOURCES.keys())
    for fname in os.listdir(downloads):
        if not fname.lower().endswith('.pdf'):
            continue
        lower = fname.lower()
        bank_hit = next((b for b in bank_codes if f"{b}" in lower), None)
        if not bank_hit:
            continue
        # year guess
        m4 = re.search(r"(20\d{2})", fname)
        year = None
        if m4:
            year = int(m4.group(1))
        else:
            m2 = re.search(r"fy(\d{2})", lower)
            if m2:
                year = 2000 + int(m2.group(1))
        if not year:
            continue
        min_year, max_year = _year_bounds()
        if not (min_year <= year <= max_year):
            continue
        src = os.path.join(downloads, fname)
        dest = build_report_path(bank_hit, year)
        try:
            ensure_directory(os.path.dirname(dest))
            shutil.copyfile(src, dest)
            if is_likely_financial_report(dest, bank_hit, year):
                moved.append(dest)
            else:
                os.remove(dest)
        except OSError:
            pass
    update_index()
    return {"moved": moved}


