"""
Bank PDF Scraper (minimal scaffold)

This module finds and downloads PDF files linked from a starting URL using
requests + BeautifulSoup. It is intentionally simple and unauthenticated.

How you'll evolve it later:
- Handle authenticated sessions (login forms, cookies).
- Add domain allow-lists and robust URL normalization.
- Add rate limiting and retries.
- Persist discovered links and metadata to SQLite.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List
import os
import pathlib
import re
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup


PDF_LINK_REGEX = re.compile(r"\.pdf($|\?|#)", re.IGNORECASE)


@dataclass
class DownloadResult:
    url: str
    output_path: str
    ok: bool
    status_code: int | None
    error: str | None


def _ensure_directory(path: str | os.PathLike) -> None:
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def _unique_destination(directory: pathlib.Path, filename: str) -> pathlib.Path:
    destination = directory / filename
    if not destination.exists():
        return destination
    stem = destination.stem
    suffix = destination.suffix
    for index in range(1, 1000):
        candidate = directory / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError("Too many conflicting filenames while saving PDFs.")


def find_pdf_links(start_url: str, html: str) -> List[str]:
    """Return absolute URLs of PDF links discovered in the provided HTML."""
    soup = BeautifulSoup(html, "html.parser")
    links: List[str] = []
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        if not href:
            continue
        if PDF_LINK_REGEX.search(href):
            absolute = urllib.parse.urljoin(start_url, href)
            links.append(absolute)
    # De-duplicate while preserving order
    seen = set()
    unique_links: List[str] = []
    for link in links:
        if link not in seen:
            unique_links.append(link)
            seen.add(link)
    return unique_links


def download_pdfs(start_url: str, output_dir: str, timeout_seconds: int = 20) -> List[DownloadResult]:
    """
    Discover and download PDFs linked from a starting web page.

    Returns a list of DownloadResult objects describing success/failure for each
    attempted download.
    """
    _ensure_directory(output_dir)
    output_directory = pathlib.Path(output_dir)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })

    try:
        response = session.get(start_url, timeout=timeout_seconds)
        response.raise_for_status()
    except Exception as exc:  # broad but intentional for scaffold
        return [DownloadResult(url=start_url, output_path="", ok=False, status_code=None, error=str(exc))]

    pdf_links = find_pdf_links(start_url, response.text)
    results: List[DownloadResult] = []

    for link in pdf_links:
        try:
            pdf_response = session.get(link, stream=True, timeout=timeout_seconds)
            status = pdf_response.status_code
            if status != 200:
                results.append(DownloadResult(url=link, output_path="", ok=False, status_code=status, error=f"HTTP {status}"))
                continue

            parsed = urllib.parse.urlparse(link)
            filename = pathlib.Path(parsed.path).name or f"download_{int(time.time())}.pdf"
            destination = _unique_destination(output_directory, filename)

            with open(destination, "wb") as file_out:
                for chunk in pdf_response.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        file_out.write(chunk)

            results.append(DownloadResult(url=link, output_path=str(destination), ok=True, status_code=status, error=None))
        except Exception as exc:  # scaffold-level error handling
            results.append(DownloadResult(url=link, output_path="", ok=False, status_code=None, error=str(exc)))

    return results


__all__ = [
    "DownloadResult",
    "find_pdf_links",
    "download_pdfs",
]
