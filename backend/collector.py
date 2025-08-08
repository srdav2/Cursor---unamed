import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from scraper import ensure_directory, extract_year_candidates
import shutil


logger = logging.getLogger(__name__)


# Map bank codes to likely investor relations pages that list annual reports.
# This list can be expanded over time.
BANK_SOURCES: Dict[str, List[str]] = {
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


def discover_annual_reports(bank: str) -> List[Tuple[int, str, str]]:
    """
    Discover candidate (year, pdf_url, label) tuples for a bank from configured sources.
    """
    sources = BANK_SOURCES.get(bank.lower(), [])
    results: List[Tuple[int, str, str]] = []
    for src in sources:
        try:
            r = http_get(src)
            soup = BeautifulSoup(r.text, "html.parser")

            # Collect direct PDF links
            pdf_links = extract_pdf_links_from_html(r.text, src)
            for url, label in pdf_links:
                text = url + " " + label
                years = extract_year_candidates(text)
                if not years:
                    continue
                # Take the most likely year embedded
                year = max(years)
                # Accept any PDF with a year; will be filtered by top N later
                results.append((year, url, label))

            # Also follow candidate detail pages (non-PDF) that likely contain annual report PDFs
            candidate_pages: List[str] = []
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                abs_url = urljoin(src, href)
                if abs_url.lower().endswith(".pdf"):
                    continue
                label = (a.get_text(" ", strip=True) or "").lower()
                if re.search(r"annual\s+report|annual\s+review|form\s+10-?k", label) or re.search(r"annual\s+report", abs_url, re.IGNORECASE):
                    candidate_pages.append(abs_url)

            # Depth-1: fetch candidate pages and extract PDFs
            for page_url in list(set(candidate_pages))[:12]:  # safety cap
                try:
                    pr = http_get(page_url)
                    sub_pdfs = extract_pdf_links_from_html(pr.text, page_url)
                    for url, label in sub_pdfs:
                        text = url + " " + label
                        years = extract_year_candidates(text)
                        if not years:
                            continue
                        year = max(years)
                        # Accept PDFs with year, regardless of label keywords
                        results.append((year, url, label))
                except Exception as exc:  # noqa: BLE001
                    logger.debug("Skip candidate page %s: %s", page_url, exc)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to parse %s: %s", src, exc)
    # Deduplicate by (year, url)
    dedup: Dict[Tuple[int, str], Tuple[int, str, str]] = {}
    for y, u, l in results:
        dedup[(y, u)] = (y, u, l)
    return sorted(dedup.values(), key=lambda t: t[0], reverse=True)


def choose_latest_n_years(candidates: List[Tuple[int, str, str]], n: int = 6) -> List[Tuple[int, str, str]]:
    # Sort by year desc and pick top distinct years
    seen: set[int] = set()
    chosen: List[Tuple[int, str, str]] = []
    for year, url, label in sorted(candidates, key=lambda t: t[0], reverse=True):
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


def build_report_path(bank: str, year: int) -> str:
    directory = os.path.join("data", "reports", bank.lower())
    ensure_directory(directory)
    filename = f"{bank.lower()}_FY{year}_Annual_Report.pdf"
    return os.path.join(directory, filename)


def update_index(index_path: str = "data/index.json") -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    base_dir = os.path.join("data", "reports")
    index: Dict[str, Dict[str, List[Dict[str, str]]]] = {}
    if not os.path.exists(base_dir):
        return index
    for bank in os.listdir(base_dir):
        bank_dir = os.path.join(base_dir, bank)
        if not os.path.isdir(bank_dir):
            continue
        entries: List[Dict[str, str]] = []
        for fname in os.listdir(bank_dir):
            if not fname.lower().endswith(".pdf"):
                continue
            m = re.match(rf"{re.escape(bank)}_FY(20\d\d)_Annual_Report\.pdf$", fname, re.IGNORECASE)
            if not m:
                continue
            year = m.group(1)
            entries.append({
                "year": year,
                "path": os.path.join("data", "reports", bank, fname),
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
        try:
            download_file(url, dest)
            saved.append({"year": str(year), "path": dest})
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed downloading %s %s: %s", bank, year, exc)
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
                download_file(url, dest)
            else:
                # treat as local file path
                if os.path.exists(url):
                    ensure_directory(os.path.dirname(dest))
                    shutil.copyfile(url, dest)
                else:
                    logger.warning("Local path not found: %s", url)
                    continue
            saved.append({"year": str(year), "path": dest})
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to ingest %s %s: %s", bank, year, exc)
    update_index()
    return {"reports": saved}


