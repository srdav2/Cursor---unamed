import json
import os
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

import fitz  # PyMuPDF

DATA_ROOT = "/workspace/data"
METRICS_DIR = os.path.join(DATA_ROOT, "metrics")
INDEX_PATH = os.path.join(DATA_ROOT, "index.json")

os.makedirs(METRICS_DIR, exist_ok=True)


@dataclass
class ExtractedMetric:
    metric_code: str
    name: str
    value: float
    currency: Optional[str]
    unit: Optional[str]
    method: str
    confidence: float
    page_index: int
    bbox: Optional[Tuple[float, float, float, float]]
    source_text: str


_MVP_PATTERNS = [
    ("NII", "Net interest income", re.compile(r"net\s+interest\s+income\s*[:\-]?\s*([\d,\.]+)", re.I)),
    ("TOTAL_LOANS", "Total loans", re.compile(r"total\s+loans\s*[:\-]?\s*([\d,\.]+)", re.I)),
]


def _load_index() -> dict:
    if not os.path.exists(INDEX_PATH):
        return {}
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def _get_pdf_path(document_id: str) -> Optional[str]:
    idx = _load_index()
    entry = idx.get(document_id)
    if not entry:
        return None
    return entry.get("pdf_path")


def _to_float(num_str: str) -> Optional[float]:
    num_str = num_str.replace(",", "").strip()
    try:
        return float(num_str)
    except Exception:  # noqa: BLE001
        return None


def _find_bbox(page: fitz.Page, needle: str) -> Optional[Tuple[float, float, float, float]]:
    try:
        rects = page.search_for(needle, quads=False)
        if rects:
            r = rects[0]
            return (r.x0, r.y0, r.x1, r.y1)
    except Exception:  # noqa: BLE001
        return None
    return None


def extract_document(document_id: str) -> List[ExtractedMetric]:
    pdf_path = _get_pdf_path(document_id)
    if not pdf_path or not os.path.exists(pdf_path):
        raise FileNotFoundError("PDF not found for document id")

    doc = fitz.open(pdf_path)
    results: List[ExtractedMetric] = []

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        text = page.get_text("text") or ""
        for code, name, pattern in _MVP_PATTERNS:
            for match in pattern.finditer(text):
                raw = match.group(1)
                value = _to_float(raw)
                if value is None:
                    continue
                bbox = _find_bbox(page, raw) or _find_bbox(page, name)
                results.append(
                    ExtractedMetric(
                        metric_code=code,
                        name=name,
                        value=value,
                        currency=None,
                        unit=None,
                        method="regex_text",
                        confidence=0.7 if bbox else 0.5,
                        page_index=page_index,
                        bbox=bbox,
                        source_text=match.group(0),
                    )
                )

    return results


def save_metrics(document_id: str, metrics: List[ExtractedMetric]) -> str:
    payload = {
        "document_id": document_id,
        "metrics": [m.__dict__ for m in metrics],
    }
    out_path = os.path.join(METRICS_DIR, f"{document_id}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return out_path


def load_metrics(document_id: str) -> Optional[dict]:
    path = os.path.join(METRICS_DIR, f"{document_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)