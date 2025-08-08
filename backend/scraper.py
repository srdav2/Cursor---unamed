import argparse
import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# pdfplumber is required for PDF parsing
import pdfplumber


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
    main()


