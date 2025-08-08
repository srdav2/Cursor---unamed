"""
PDF Processor (minimal scaffold)

Uses pdfplumber to extract tables (if present) from a PDF file and returns a
list of pandas DataFrames. This is a starting point and may need to be tailored
for specific bank statement formats.

How you'll evolve it later:
- Custom table settings per bank/template.
- Extract plain text when tables are absent.
- Normalize/clean columns, data types, and currencies.
- Persist parsed tables to SQLite.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import pandas as pd
import pdfplumber


@dataclass
class ExtractedCell:
    document_path: str
    page_index: int  # zero-based
    value: str
    row_index: int
    col_index: int
    bbox: tuple[float, float, float, float] | None  # (x0, top, x1, bottom) in PDF points
    section_hint: str | None


def extract_tables_with_metadata(pdf_path: str) -> List[ExtractedCell]:
    """Extract table cells with page and approximate bbox metadata for QC screenshots."""
    results: List[ExtractedCell] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            page_tables = page.find_tables() or []
            for table in page_tables:
                # Table cells are in table.cells with bbox metadata
                # Fallback: if table.cells is not available, use extract_tables
                if hasattr(table, "cells") and table.cells:
                    # Build a grid map of (row, col) -> cell bbox and text
                    for cell in table.cells:
                        text = (cell.get("text") or "").strip()
                        if text == "":
                            continue
                        r = int(cell.get("row_idx", -1))
                        c = int(cell.get("col_idx", -1))
                        bbox = cell.get("bbox")  # (x0, top, x1, bottom)
                        results.append(
                            ExtractedCell(
                                document_path=pdf_path,
                                page_index=page_index,
                                value=text,
                                row_index=r,
                                col_index=c,
                                bbox=bbox,
                                section_hint=None,
                            )
                        )
                else:
                    # Fallback mode: approximate bbox by using words boxes per cell
                    raw_tables = page.extract_tables() or []
                    for raw_table in raw_tables:
                        headers = raw_table[0] if raw_table and len(raw_table) > 1 else None
                        for r_idx, row in enumerate(raw_table[1:] if headers else raw_table):
                            for c_idx, cell_text in enumerate(row):
                                text = (cell_text or "").strip()
                                if text == "":
                                    continue
                                # Approximate bbox by union of words matching the text (best-effort)
                                words = page.extract_words(keep_blank_chars=False)
                                matching_words = [w for w in words if w.get("text") in text]
                                if matching_words:
                                    x0 = min(w["x0"] for w in matching_words)
                                    top = min(w["top"] for w in matching_words)
                                    x1 = max(w["x1"] for w in matching_words)
                                    bottom = max(w["bottom"] for w in matching_words)
                                    bbox = (x0, top, x1, bottom)
                                else:
                                    bbox = None
                                results.append(
                                    ExtractedCell(
                                        document_path=pdf_path,
                                        page_index=page_index,
                                        value=text,
                                        row_index=r_idx,
                                        col_index=c_idx,
                                        bbox=bbox,
                                        section_hint=None,
                                    )
                                )
    return results


def extract_tables_to_dataframes(pdf_path: str) -> List[pd.DataFrame]:
    """Return a list of DataFrames, one per detected table across all pages."""
    tables: List[pd.DataFrame] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_tables = page.extract_tables() or []
            for raw_table in page_tables:
                if not raw_table or all(row is None for row in raw_table):
                    continue
                headers = raw_table[0]
                body = raw_table[1:] if len(raw_table) > 1 else []
                try:
                    df = pd.DataFrame(body, columns=headers)
                except Exception:
                    df = pd.DataFrame(raw_table)
                tables.append(df)
    return tables


<<<<<<< Current (Your changes)
__all__ = ["extract_tables_to_dataframes"]
=======
__all__ = [
    "ExtractedCell",
    "extract_tables_with_metadata",
    "extract_tables_to_dataframes",
]
>>>>>>> Incoming (Background Agent changes)
