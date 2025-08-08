from __future__ import annotations

import os
import pathlib
import sqlite3
from typing import Iterable, List

from .processors.pdf_processor import extract_tables_with_metadata, ExtractedCell
from .processors.screenshotter import render_cell_screenshot, ensure_directory

# Paths
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
PDF_DIR = DATA_DIR / "pdfs"
SCREENSHOT_DIR = DATA_DIR / "screenshots"
DB_PATH = DATA_DIR / "qc.db"


def ensure_db() -> None:
    ensure_directory(str(DATA_DIR))
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS extracted_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_path TEXT NOT NULL,
                page_index INTEGER NOT NULL,
                value TEXT,
                row_index INTEGER,
                col_index INTEGER,
                bbox_x0 REAL,
                bbox_top REAL,
                bbox_x1 REAL,
                bbox_bottom REAL,
                screenshot_path TEXT,
                section_hint TEXT,
                validated INTEGER DEFAULT 0,
                validated_by TEXT,
                validated_at TEXT
            )
            """
        )


def iter_pdfs(pdf_dir: pathlib.Path) -> Iterable[pathlib.Path]:
    if not pdf_dir.exists():
        return []
    for path in pdf_dir.glob("**/*.pdf"):
        if path.is_file():
            yield path


def process_pdf(pdf_path: pathlib.Path) -> List[int]:
    """Process a single PDF, return inserted row IDs."""
    cells = extract_tables_with_metadata(str(pdf_path))
    inserted_ids: List[int] = []
    if not cells:
        return inserted_ids

    # Per-document screenshot directory
    doc_base = pdf_path.stem
    doc_screenshot_dir = SCREENSHOT_DIR / doc_base
    ensure_directory(str(doc_screenshot_dir))

    with sqlite3.connect(DB_PATH) as conn:
        for cell in cells:
            # Render screenshot if bbox present
            screenshot_path = None
            if cell.bbox:
                filename = f"page{cell.page_index + 1}_r{cell.row_index}_c{cell.col_index}.png"
                out_path = doc_screenshot_dir / filename
                try:
                    render_cell_screenshot(
                        pdf_path=str(pdf_path),
                        page_index=cell.page_index,
                        bbox=cell.bbox,
                        output_path=str(out_path),
                    )
                    screenshot_path = str(out_path)
                except Exception:
                    screenshot_path = None

            cur = conn.execute(
                """
                INSERT INTO extracted_items (
                    document_path, page_index, value, row_index, col_index,
                    bbox_x0, bbox_top, bbox_x1, bbox_bottom,
                    screenshot_path, section_hint, validated, validated_by, validated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, NULL, NULL)
                """,
                (
                    str(pdf_path),
                    cell.page_index,
                    cell.value,
                    cell.row_index,
                    cell.col_index,
                    (cell.bbox[0] if cell.bbox else None),
                    (cell.bbox[1] if cell.bbox else None),
                    (cell.bbox[2] if cell.bbox else None),
                    (cell.bbox[3] if cell.bbox else None),
                    screenshot_path,
                    cell.section_hint,
                ),
            )
            inserted_ids.append(cur.lastrowid)
        conn.commit()
    return inserted_ids


def run_qc_pipeline(pdf_dir: str | None = None) -> int:
    ensure_db()
    base = pathlib.Path(pdf_dir) if pdf_dir else PDF_DIR
    ensure_directory(str(base))
    total_inserted = 0
    for pdf_path in iter_pdfs(base):
        ids = process_pdf(pdf_path)
        total_inserted += len(ids)
    return total_inserted


__all__ = ["run_qc_pipeline", "process_pdf", "ensure_db", "DB_PATH", "SCREENSHOT_DIR"]
