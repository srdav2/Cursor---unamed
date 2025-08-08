import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# pdfplumber is required for PDF parsing and rendering
import pdfplumber
import pandas as pd
from rapidfuzz import fuzz, process as rf_process
from unidecode import unidecode


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
)


BANK_SITES: Dict[str, List[str]] = {
    # Commonwealth Bank of Australia – annual reports/financials hub
    "cba": [
        "https://www.commbank.com.au/about-us/investors/financials/annual-reports.html",
        "https://www.commbank.com.au/about-us/investors/financials.html",
    ],
    # National Australia Bank – annual report hub
    "nab": [
        "https://www.nab.com.au/about-us/company/who-we-are/annual-report",
        "https://www.nab.com.au/about-us/company/investor-centre/annual-reports",
    ],
}


# Our Standardized Schema for Key Metrics
# This will be expanded over time.
FINANCIAL_SCHEMA: List[Dict[str, Any]] = [
    {
        "standard_name": "net_interest_income",
        "search_terms": ["Net interest income", "Interest income, net"],
        "value_kind": "amount",
    },
    {
        "standard_name": "operating_income",
        "search_terms": ["Operating income", "Total operating income"],
        "value_kind": "amount",
    },
    {
        "standard_name": "loan_impairment_expense",
        "search_terms": ["Loan impairment expense", "Provision for credit losses"],
        "value_kind": "amount",
    },
    {
        "standard_name": "operating_expenses",
        "search_terms": ["Operating expenses", "Total operating expenses", "Expenses"],
        "value_kind": "amount",
    },
    {
        "standard_name": "net_profit_after_tax",
        "search_terms": [
            "Net profit after tax",
            "Profit for the year attributable to equity holders",
        ],
        "value_kind": "amount",
    },
    {
        "standard_name": "total_assets",
        "search_terms": ["Total assets"],
        "value_kind": "amount",
    },
    {
        "standard_name": "total_liabilities",
        "search_terms": ["Total liabilities"],
        "value_kind": "amount",
    },
    {
        "standard_name": "total_equity",
        "search_terms": ["Total equity", "Shareholders' equity", "Equity attributable to"],
        "value_kind": "amount",
    },
    {
        "standard_name": "customer_deposits",
        "search_terms": ["Customer deposits", "Deposits from customers"],
        "value_kind": "amount",
    },
    {
        "standard_name": "loans_and_advances",
        "search_terms": ["Loans and advances", "Net loans", "Gross loans and advances"],
        "value_kind": "amount",
    },
    {
        "standard_name": "net_cash_from_operating",
        "search_terms": [
            "Net cash from operating activities",
            "Net cash provided by operating activities",
        ],
        "value_kind": "amount",
    },
    {
        "standard_name": "nim",
        "search_terms": ["Net interest margin", "NIM"],
        "value_kind": "ratio",
    },
    {
        "standard_name": "cost_income_ratio",
        "search_terms": ["Cost to income ratio", "Cost/income ratio"],
        "value_kind": "ratio",
    },
    {
        "standard_name": "roe",
        "search_terms": ["Return on equity", "ROE"],
        "value_kind": "ratio",
    },
    {
        "standard_name": "roa",
        "search_terms": ["Return on assets", "ROA"],
        "value_kind": "ratio",
    },
    {
        "standard_name": "cet1_ratio",
        "search_terms": ["CET1 ratio", "Common Equity Tier 1 ratio"],
        "value_kind": "ratio",
    },
    {
        "standard_name": "lcr",
        "search_terms": ["Liquidity coverage ratio", "LCR"],
        "value_kind": "ratio",
    },
]


# Bank registry: metadata for geography, continent, and reporting currency
BANK_REGISTRY: Dict[str, Dict[str, Any]] = {
    # Australia
    "cba": {"name": "Commonwealth Bank of Australia", "country": "Australia", "continent": "Oceania", "reporting_currency": "AUD"},
    "nab": {"name": "National Australia Bank Limited", "country": "Australia", "continent": "Oceania", "reporting_currency": "AUD"},
    "wbc": {"name": "Westpac Banking Corporation", "country": "Australia", "continent": "Oceania", "reporting_currency": "AUD"},
    "anz": {"name": "Australia and New Zealand Banking Group Limited", "country": "Australia", "continent": "Oceania", "reporting_currency": "AUD"},
    "mqg": {"name": "Macquarie Group Limited", "country": "Australia", "continent": "Oceania", "reporting_currency": "AUD"},

    # Canada
    "rbc": {"name": "Royal Bank of Canada", "country": "Canada", "continent": "North America", "reporting_currency": "CAD"},
    "td": {"name": "Toronto-Dominion Bank", "country": "Canada", "continent": "North America", "reporting_currency": "CAD"},
    "bns": {"name": "The Bank of Nova Scotia", "country": "Canada", "continent": "North America", "reporting_currency": "CAD"},
    "bmo": {"name": "Bank of Montreal", "country": "Canada", "continent": "North America", "reporting_currency": "CAD"},
    "cm": {"name": "Canadian Imperial Bank of Commerce", "country": "Canada", "continent": "North America", "reporting_currency": "CAD"},
    "nbc": {"name": "National Bank of Canada", "country": "Canada", "continent": "North America", "reporting_currency": "CAD"},

    # United States
    "jpm": {"name": "JPMorgan Chase & Co.", "country": "United States", "continent": "North America", "reporting_currency": "USD"},
    "bac": {"name": "Bank of America Corporation", "country": "United States", "continent": "North America", "reporting_currency": "USD"},
    "wfc": {"name": "Wells Fargo & Company", "country": "United States", "continent": "North America", "reporting_currency": "USD"},
    "c": {"name": "Citigroup Inc.", "country": "United States", "continent": "North America", "reporting_currency": "USD"},
    "gs": {"name": "The Goldman Sachs Group, Inc.", "country": "United States", "continent": "North America", "reporting_currency": "USD"},
    "ms": {"name": "Morgan Stanley", "country": "United States", "continent": "North America", "reporting_currency": "USD"},

    # United Kingdom
    "hsbc": {"name": "HSBC Holdings plc", "country": "United Kingdom", "continent": "Europe", "reporting_currency": "USD"},
    "barc": {"name": "Barclays PLC", "country": "United Kingdom", "continent": "Europe", "reporting_currency": "GBP"},
    "lloy": {"name": "Lloyds Banking Group plc", "country": "United Kingdom", "continent": "Europe", "reporting_currency": "GBP"},
    "nwg": {"name": "NatWest Group plc", "country": "United Kingdom", "continent": "Europe", "reporting_currency": "GBP"},
    "stan": {"name": "Standard Chartered PLC", "country": "United Kingdom", "continent": "Europe", "reporting_currency": "USD"},

    # Eurozone
    "bnpp": {"name": "BNP Paribas", "country": "France", "continent": "Europe", "reporting_currency": "EUR"},
    "aca": {"name": "Crédit Agricole", "country": "France", "continent": "Europe", "reporting_currency": "EUR"},
    "san": {"name": "Banco Santander, S.A.", "country": "Spain", "continent": "Europe", "reporting_currency": "EUR"},
    "ing": {"name": "ING Groep N.V.", "country": "Netherlands", "continent": "Europe", "reporting_currency": "EUR"},
    "dbk": {"name": "Deutsche Bank AG", "country": "Germany", "continent": "Europe", "reporting_currency": "EUR"},
    "isp": {"name": "Intesa Sanpaolo S.p.A.", "country": "Italy", "continent": "Europe", "reporting_currency": "EUR"},

    # Switzerland
    "ubs": {"name": "UBS Group AG", "country": "Switzerland", "continent": "Europe", "reporting_currency": "USD"},

    # Japan
    "mufg": {"name": "Mitsubishi UFJ Financial Group, Inc.", "country": "Japan", "continent": "Asia", "reporting_currency": "JPY"},
    "smfg": {"name": "Sumitomo Mitsui Financial Group, Inc.", "country": "Japan", "continent": "Asia", "reporting_currency": "JPY"},
    "mizuho": {"name": "Mizuho Financial Group, Inc.", "country": "Japan", "continent": "Asia", "reporting_currency": "JPY"},

    # China
    "icbc": {"name": "Industrial and Commercial Bank of China", "country": "China", "continent": "Asia", "reporting_currency": "CNY"},
    "ccb": {"name": "China Construction Bank Corporation", "country": "China", "continent": "Asia", "reporting_currency": "CNY"},
    "abc": {"name": "Agricultural Bank of China", "country": "China", "continent": "Asia", "reporting_currency": "CNY"},
    "boc": {"name": "Bank of China", "country": "China", "continent": "Asia", "reporting_currency": "CNY"},

    # Singapore
    "dbs": {"name": "DBS Group Holdings Ltd", "country": "Singapore", "continent": "Asia", "reporting_currency": "SGD"},
    "ocbc": {"name": "Oversea-Chinese Banking Corporation Limited", "country": "Singapore", "continent": "Asia", "reporting_currency": "SGD"},
    "uob": {"name": "United Overseas Bank Limited", "country": "Singapore", "continent": "Asia", "reporting_currency": "SGD"},
}


def ensure_directory(directory_path: str) -> None:
    if directory_path and not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


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


def extract_year_candidates(text: str) -> List[int]:
    years = re.findall(r"(20\d{2})", text)
    return [int(y) for y in years]


def find_annual_report_pdf_links(html: str, base_url: str) -> List[Tuple[str, str]]:
    """
    Returns list of (absolute_pdf_url, anchor_text) candidates found on the page.
    Prioritizes anchors that suggest annual reports.
    """
    soup = BeautifulSoup(html, "html.parser")
    candidates: List[Tuple[str, str]] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        abs_url = urljoin(base_url, href)
        if not abs_url.lower().endswith(".pdf"):
            continue
        text = a.get_text(" ", strip=True) or ""
        label = text.lower()
        if ("annual" in label and "report" in label) or ("annual report" in abs_url.lower()):
            candidates.append((abs_url, text))
    return candidates


def select_best_pdf_url(candidates: List[Tuple[str, str]], year: Optional[int]) -> Optional[str]:
    if not candidates:
        return None
    if year is None:
        # pick the candidate with the largest year found; fallback to first
        annotated: List[Tuple[str, str, Optional[int]]] = []
        for url, text in candidates:
            years = extract_year_candidates(url + " " + text)
            annotated.append((url, text, max(years) if years else None))
        annotated.sort(key=lambda x: (x[2] or 0), reverse=True)
        return annotated[0][0]
    # try to find exact match for requested year; else closest below
    exact: List[Tuple[str, str]] = []
    with_year: List[Tuple[str, str, int]] = []
    for url, text in candidates:
        years = extract_year_candidates(url + " " + text)
        if year in years:
            exact.append((url, text))
        elif years:
            with_year.append((url, text, max(years)))
    if exact:
        # prefer first exact match
        return exact[0][0]
    if with_year:
        # sort by year descending but <= requested year
        filtered = [c for c in with_year if c[2] <= year]
        if filtered:
            filtered.sort(key=lambda x: x[2], reverse=True)
            return filtered[0][0]
    # fallback
    return candidates[0][0]


def get_annual_report_url(bank: str, year: Optional[int]) -> Optional[str]:
    bank_key = bank.lower()
    if bank_key not in BANK_SITES:
        raise ValueError(f"Unsupported bank code: {bank}")
    for page_url in BANK_SITES[bank_key]:
        try:
            logging.info(f"Fetching index page: {page_url}")
            resp = http_get(page_url)
            candidates = find_annual_report_pdf_links(resp.text, page_url)
            if not candidates:
                continue
            selected = select_best_pdf_url(candidates, year)
            if selected:
                logging.info(f"Selected annual report URL: {selected}")
                return selected
        except Exception as exc:  # noqa: BLE001
            logging.warning(f"Failed to process {page_url}: {exc}")
            continue
    return None


def download_pdf(url: str, dest_path: str) -> str:
    ensure_directory(os.path.dirname(dest_path))
    logging.info(f"Downloading PDF: {url}")
    with requests.get(url, stream=True) as r:  # type: ignore[call-arg]
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    logging.info(f"Saved PDF to: {dest_path}")
    return dest_path


def is_numeric_token(text: str) -> bool:
    candidate = text.replace("\u2212", "-")  # replace unicode minus
    return bool(re.match(r"^[\$\(\-\+]?\d[\d,\.]*[%\)]?$", candidate))


def join_numeric_sequence(words: List[Dict[str, Any]], start_index: int) -> Tuple[str, Tuple[float, float, float, float]]:
    """
    Join consecutive numeric-like tokens to form a value string and compute its bounding box.
    Returns (value_text, (x0, top, x1, bottom)).
    """
    if start_index < 0 or start_index >= len(words):
        return "", (0.0, 0.0, 0.0, 0.0)
    x0 = float(words[start_index]["x0"])  # type: ignore[index]
    top = float(words[start_index]["top"])  # type: ignore[index]
    bottom = float(words[start_index]["bottom"])  # type: ignore[index]
    value_parts: List[str] = []
    last_right = float(words[start_index]["x1"])  # type: ignore[index]
    i = start_index
    while i < len(words) and is_numeric_token(words[i]["text"]):  # type: ignore[index]
        w = words[i]
        value_parts.append(str(w["text"]))
        last_right = float(w["x1"])  # type: ignore[index]
        bottom = max(bottom, float(w["bottom"]))  # type: ignore[index]
        i += 1
    value_text = " ".join(value_parts)
    return value_text, (x0, top, last_right, bottom)


def find_phrase_indices(words: List[Dict[str, Any]], phrase: str) -> List[Tuple[int, int]]:
    """
    Find all matched (start_index, end_index_exclusive) for phrase across words.
    Matching is case-insensitive on whitespace-normalized text.
    """
    tokens = [w["text"].strip().lower() for w in words]
    phrase_tokens = [t for t in re.split(r"\s+", phrase.strip().lower()) if t]
    n = len(tokens)
    m = len(phrase_tokens)
    matches: List[Tuple[int, int]] = []
    for i in range(n - m + 1):
        if tokens[i : i + m] == phrase_tokens:
            matches.append((i, i + m))
    return matches


def find_value_near_phrase(words: List[Dict[str, Any]], match_span: Tuple[int, int]) -> Optional[Tuple[str, Tuple[float, float, float, float]]]:
    """
    Given a phrase match span, search rightwards on the same line for the first numeric sequence.
    """
    start, end = match_span
    if end >= len(words):
        return None
    phrase_last_word = words[end - 1]
    target_top = float(phrase_last_word["top"])  # type: ignore[index]
    target_bottom = float(phrase_last_word["bottom"])  # type: ignore[index]
    # Tolerance for same-line grouping
    y_tol = max(2.0, (target_bottom - target_top) * 1.5)
    right_min_x = float(phrase_last_word["x1"])  # type: ignore[index]
    # Scan subsequent words to the right on roughly the same y band
    for i in range(end, len(words)):
        w = words[i]
        top = float(w["top"])  # type: ignore[index]
        bottom = float(w["bottom"])  # type: ignore[index]
        x0 = float(w["x0"])  # type: ignore[index]
        if abs(top - target_top) <= y_tol and x0 >= right_min_x:
            if is_numeric_token(w["text"]):  # type: ignore[index]
                return join_numeric_sequence(words, i)
    return None


def normalize_label(text: str) -> str:
    # Lowercase, remove accents, condense spaces and punctuation to spaces
    t = unidecode(text).lower()
    t = re.sub(r"[^a-z0-9%\-\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def fuzzy_label_match(label: str, candidates: List[str]) -> Tuple[Optional[str], int]:
    """Return best-matching candidate and score (0-100)."""
    norm_label = normalize_label(label)
    norm_candidates = [normalize_label(c) for c in candidates]
    if not norm_label or not norm_candidates:
        return None, 0
    # Use token sort ratio to be resilient to word order
    best = rf_process.extractOne(norm_label, norm_candidates, scorer=fuzz.token_sort_ratio)
    if best is None:
        return None, 0
    match_text, score, idx = best
    return candidates[idx], int(score)


def detect_units_near(page: pdfplumber.page.Page, box: Dict[str, Any]) -> Optional[str]:
    """Search above the term for a units hint like '$m', 'million', 'bn', '%'."""
    top = float(box.get("top", box.get("y0", 0)))
    left = max(0.0, float(box.get("x0", 0)) - 150)
    right = min(page.width, float(box.get("x1", page.width)) + 150)
    band_top = max(0.0, top - 60)
    cropped = page.crop((left, band_top, right, top))
    text = (cropped.extract_text() or "").lower()
    if not text:
        return None
    # Common unit cues
    if re.search(r"\b(thousands|000s)\b", text):
        return "thousands"
    if re.search(r"\b(million|\$m|aud m|aud million|in millions)\b", text):
        return "millions"
    if re.search(r"\b(billion|\$bn|aud bn|aud billion|in billions)\b", text):
        return "billions"
    if "%" in text:
        return "%"
    return None


def normalize_value_by_units(value: float, units: Optional[str]) -> float:
    if not units:
        return value
    if units == "thousands":
        return value * 1_000
    if units == "millions":
        return value * 1_000_000
    if units == "billions":
        return value * 1_000_000_000
    return value


def extract_kpis_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Extract a small set of KPIs and their approximate coordinates from the PDF.
    Returns a dictionary ready for JSON serialization.
    """
    kpi_targets = {
        "net_interest_income": [
            "net interest income",
        ],
        "net_profit_after_tax": [
            "net profit after tax",
            "profit after income tax",
            "statutory net profit after tax",
        ],
    }

    results: Dict[str, Dict[str, Any]] = {
        "net_interest_income": {"value": None, "page": None, "bbox": None, "label_bbox": None},
        "net_profit_after_tax": {"value": None, "page": None, "bbox": None, "label_bbox": None},
    }

    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            try:
                words = page.extract_words(
                    use_text_flow=True,
                    keep_blank_chars=False,
                ) or []
            except Exception as exc:  # noqa: BLE001
                logging.warning(f"Failed to extract words on page {page_index + 1}: {exc}")
                continue

            if not words:
                continue

            for kpi_key, phrases in kpi_targets.items():
                # skip if already found
                if results[kpi_key]["value"] is not None:
                    continue
                for phrase in phrases:
                    matches = find_phrase_indices(words, phrase)
                    for span in matches:
                        value_hit = find_value_near_phrase(words, span)
                        label_words = words[span[0] : span[1]]
                        if label_words:
                            x0 = min(float(w["x0"]) for w in label_words)  # type: ignore[index]
                            x1 = max(float(w["x1"]) for w in label_words)  # type: ignore[index]
                            top = min(float(w["top"]) for w in label_words)  # type: ignore[index]
                            bottom = max(float(w["bottom"]) for w in label_words)  # type: ignore[index]
                            label_bbox = (x0, top, x1, bottom)
                        else:
                            label_bbox = None

                        if value_hit is not None:
                            value_text, value_bbox = value_hit
                            results[kpi_key] = {
                                "value": value_text,
                                "page": page_index + 1,  # 1-based
                                "bbox": value_bbox,
                                "label_bbox": label_bbox,
                            }
                            break
                    if results[kpi_key]["value"] is not None:
                        break

    return results


def _clean_number_string(value_str: str) -> Optional[float]:
    s = value_str.strip()
    # Convert accounting negatives (parentheses) to minus sign
    s = s.replace(",", "").replace("\u2212", "-")
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    # Remove currency symbols and percentage if present for numeric parsing
    s = re.sub(r"[$%]", "", s)
    try:
        return float(s)
    except Exception:  # noqa: BLE001
        return None


def detect_currency_near(page: pdfplumber.page.Page, box: Dict[str, Any]) -> Optional[str]:
    """Detect likely currency near a label: $, A$, C$, US$, NZ$, €, £, ¥ and textual cues."""
    top = float(box.get("top", box.get("y0", 0)))
    left = max(0.0, float(box.get("x0", 0)) - 200)
    right = min(page.width, float(box.get("x1", page.width)) + 200)
    band_top = max(0.0, top - 80)
    cropped = page.crop((left, band_top, right, top))
    text = (cropped.extract_text() or "").lower()
    if not text:
        return None
    # Symbol cues
    if "aud" in text or "a$" in text:
        return "AUD"
    if "cad" in text or "c$" in text:
        return "CAD"
    if "usd" in text or "us$" in text or "$" in text:
        return "USD"
    if "eur" in text or "€" in text:
        return "EUR"
    if "gbp" in text or "£" in text:
        return "GBP"
    if "jpy" in text or "¥" in text:
        return "JPY"
    if "cny" in text or "rmb" in text:
        return "CNY"
    if "sgd" in text:
        return "SGD"
    return None


def create_qc_snippet(page: pdfplumber.page.Page, search_term: str, value_str: str, report_name: str, metric_name: str) -> Path:
    """
    Creates and saves a visual snippet of the data point from the PDF page
    for the Quality Control feature.
    """
    snippets_dir = Path("backend/qc_snippets")
    snippets_dir.mkdir(parents=True, exist_ok=True)

    term_hits = page.search(search_term, case=False) or []
    value_hits = page.search(value_str, case=False) or []

    # Fallback to using the first hit if available
    if not term_hits or not value_hits:
        # Render full page as a minimal fallback snippet
        try:
            img = page.to_image(resolution=200)
            snippet_filename = f"{report_name}_{metric_name}.png"
            snippet_path = snippets_dir / snippet_filename
            img.save(snippet_path, format="PNG")
            return snippet_path
        except Exception:  # noqa: BLE001
            return snippets_dir / f"{report_name}_{metric_name}.png"

    term_box = term_hits[0]
    value_box = value_hits[0]

    img = page.to_image(resolution=200)

    # Highlight the term in blue and the value in red
    img.draw_rect(term_box, fill=(0, 0, 255, 50), stroke=None)
    img.draw_rect(value_box, fill=(255, 0, 0, 50), stroke=None)

    crop_box = (
        min(term_box.get("x0", 0), value_box.get("x0", 0)) - 20,
        min(term_box.get("top", term_box.get("y0", 0)), value_box.get("top", value_box.get("y0", 0))) - 20,
        max(term_box.get("x1", page.width), value_box.get("x1", page.width)) + 20,
        max(term_box.get("bottom", term_box.get("y1", page.height)), value_box.get("bottom", value_box.get("y1", page.height))) + 20,
    )
    snippet_filename = f"{report_name}_{metric_name}.png"
    snippet_path = snippets_dir / snippet_filename
    img.save(snippet_path, format="PNG")
    return snippet_path


def extract_financial_data(pdf_path: Path, schema: List[Dict[str, Any]], bank: Optional[str] = None, year: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Parses a PDF file to extract financial data based on a given schema.

    Returns a list of dictionaries, where each dictionary contains the extracted
    data point and its metadata for the QC feature.
    """
    extracted_data: List[Dict[str, Any]] = []
    print(f"Processing PDF: {pdf_path.name}")

    with pdfplumber.open(str(pdf_path)) as pdf:
        for metric in schema:
            print(f"  Searching for metric: {metric['standard_name']}")
            found_metric = False
            for page_num, page in enumerate(pdf.pages):
                if found_metric:
                    break

                # Extract to warm up internal structures; might be useful for future enhancements
                _ = page.extract_tables()
                page_text = page.extract_text() or ""

                for term in metric["search_terms"]:
                    # Find the term as a whole phrase, ignoring case
                    match = re.search(r"\b" + re.escape(term) + r"\b", page_text, re.IGNORECASE)
                    if not match:
                        continue

                    # Bounding boxes for the term on page (exact search)
                    term_hits = page.search(term, case=False) or []
                    if not term_hits:
                        # Fuzzy search: scan all extracted words and pick the best fuzzy match
                        words = page.extract_words(use_text_flow=True) or []
                        if not words:
                            continue
                        label_texts = [w.get("text", "") for w in words]
                        best_label, score = fuzzy_label_match(term, label_texts)
                        if not best_label or score < 80:  # threshold to avoid spurious hits
                            continue
                        # Find bbox of the first word occurrence matching best_label
                        idx = next((i for i, w in enumerate(words) if w.get("text", "") == best_label), -1)
                        if idx == -1:
                            continue
                        term_box = {
                            "x0": words[idx]["x0"],
                            "top": words[idx]["top"],
                            "x1": words[idx]["x1"],
                            "bottom": words[idx]["bottom"],
                        }
                    else:
                        term_box = term_hits[0]

                    # Use a horizontal band around the term to search for numeric values
                    band_top = float(term_box.get("top", term_box.get("y0", 0))) - 5
                    band_bottom = float(term_box.get("bottom", term_box.get("y1", 0))) + 5
                    cropped = page.crop((0, max(0, band_top), page.width, min(page.height, band_bottom)))
                    line_text = cropped.extract_text() or ""

                    # Find numbers: handles commas, parentheses for negatives, decimals
                    number_matches = re.findall(r"\(?[\$\d,]+\)?\.?\d*%?", line_text)
                    number_matches = [n for n in number_matches if re.search(r"\d", n)]
                    if not number_matches:
                        continue

                    value_str = number_matches[0].strip()
                    value_float = _clean_number_string(value_str)
                    if value_float is None:
                        continue

                    units = detect_units_near(page, term_box)
                    currency = detect_currency_near(page, term_box)
                    normalized_value = normalize_value_by_units(value_float, units)

                    # Create the QC snippet image
                    snippet_path = create_qc_snippet(
                        page=page,
                        search_term=term,
                        value_str=value_str,
                        report_name=pdf_path.stem,
                        metric_name=metric["standard_name"],
                    )

                    data_point: Dict[str, Any] = {
                        "bank_name": bank,
                        "report_year": year,
                        "metric_name": metric["standard_name"],
                        "value": normalized_value,
                        "raw_value": value_str,
                        "value_units": units,
                        "value_currency": currency,
                        "value_kind": metric.get("value_kind", "amount"),
                        "source_page": page_num + 1,  # 1-based page numbering
                        "source_term_used": term,
                        "source_coordinates": {
                            "term_bbox": {
                                "x0": float(term_box.get("x0", 0)),
                                "top": float(term_box.get("top", term_box.get("y0", 0))),
                                "x1": float(term_box.get("x1", 0)),
                                "bottom": float(term_box.get("bottom", term_box.get("y1", 0))),
                            }
                        },
                        "snippet_path": str(snippet_path),
                        "is_validated": False,
                    }
                    extracted_data.append(data_point)
                    print(f"    -> Found: {metric['standard_name']} = {value_float}")
                    found_metric = True
                    break
    return extracted_data


def run_scraper(
    bank: Optional[str] = None,
    year: Optional[int] = None,
    url: Optional[str] = None,
    pdf_path: Optional[str] = None,
    downloads_dir: str = "data/downloads",
) -> Dict[str, Any]:
    """
    Orchestrates fetching/downloading a PDF and extracting KPI data.
    If pdf_path is provided, downloading is skipped.
    If url is provided, it is used directly. Otherwise, attempts discovery by bank/year.
    """
    if not pdf_path:
        if not url:
            if not bank:
                raise ValueError("Provide either --pdf, --url, or --bank to discover the PDF.")
            url = get_annual_report_url(bank, year)
        if not url:
            raise RuntimeError("Could not determine annual report URL.")
        # Determine filename
        filename = os.path.basename(url.split("?")[0]) or f"{bank or 'report'}_{year or ''}.pdf"
        dest_path = os.path.join(downloads_dir, filename)
        pdf_path = download_pdf(url, dest_path)
    else:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

    kpis = extract_kpis_from_pdf(pdf_path)
    result: Dict[str, Any] = {
        "source_pdf": pdf_path,
        "bank": bank,
        "year": year,
        "extracted_at": datetime.utcnow().isoformat() + "Z",
        "kpis": kpis,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Annual report PDF scraper")
    parser.add_argument("--bank", choices=sorted(BANK_SITES.keys()), help="Bank code (e.g., cba, nab)")
    parser.add_argument("--year", type=int, help="Target year (e.g., 2024)")
    parser.add_argument("--url", help="Direct URL to an annual report PDF")
    parser.add_argument("--pdf", dest="pdf_path", help="Local path to an annual report PDF (skips download)")
    parser.add_argument("--out", dest="out_path", help="Write extracted data to this JSON file")
    parser.add_argument("--downloads", dest="downloads_dir", default="data/downloads", help="Directory to save downloaded PDFs")
    args = parser.parse_args()

    try:
        result = run_scraper(
            bank=args.bank,
            year=args.year,
            url=args.url,
            pdf_path=args.pdf_path,
            downloads_dir=args.downloads_dir,
        )
    except Exception as exc:  # noqa: BLE001
        logging.error(f"Scraper failed: {exc}")
        raise

    if args.out_path:
        ensure_directory(os.path.dirname(args.out_path))
        with open(args.out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logging.info(f"Wrote output JSON: {args.out_path}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    # If no CLI args are provided, run demo mode per schema-based extraction brief
    if len(sys.argv) == 1:
        reports_dir = Path("backend/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)

        preferred = reports_dir / "cba_2024_report.pdf"
        chosen_pdf: Optional[Path] = None
        bank_guess: Optional[str] = None
        year_guess: Optional[int] = None

        if preferred.exists():
            chosen_pdf = preferred
            bank_guess = "cba"
            year_guess = 2024
        else:
            # Fallback: use first existing PDF in data/downloads for a demo run
            downloads_dir = Path("data/downloads")
            pdfs = sorted(downloads_dir.glob("*.pdf")) if downloads_dir.exists() else []
            if pdfs:
                chosen_pdf = pdfs[0]
                # naive guesses from filename
                name = chosen_pdf.stem.lower()
                if "cba" in name:
                    bank_guess = "cba"
                elif "nab" in name:
                    bank_guess = "nab"
                match_year = re.search(r"(20\d{2})", name)
                if match_year:
                    year_guess = int(match_year.group(1))

        if not chosen_pdf:
            print("Error: Please download the CBA 2024 Annual Report,")
            print("rename it to 'cba_2024_report.pdf', and place it in the")
            print("'backend/reports' directory.")
            sys.exit(1)

        data = extract_financial_data(chosen_pdf, FINANCIAL_SCHEMA, bank=bank_guess, year=year_guess)
        df = pd.DataFrame(data)

        print("\n--- Extraction Complete (Schema Mode) ---")
        if not df.empty:
            print(df.to_string(index=False))
        else:
            print("No metrics found using current schema.")

        output_csv_path = Path("backend/extracted_data.csv")
        if not df.empty:
            df.to_csv(output_csv_path, index=False)
            print(f"\nData saved to {output_csv_path}")
    else:
        # Run the original CLI for discovery/downloading + basic KPI extraction
        main()


