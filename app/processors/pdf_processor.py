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

from typing import List
import pandas as pd
import pdfplumber


def extract_tables_to_dataframes(pdf_path: str) -> List[pd.DataFrame]:
    """Return a list of DataFrames, one per detected table across all pages."""
    tables: List[pd.DataFrame] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_tables = page.extract_tables() or []
            for raw_table in page_tables:
                if not raw_table or all(row is None for row in raw_table):
                    continue
                # Assume the first row is headers when it looks like it
                headers = raw_table[0]
                body = raw_table[1:] if len(raw_table) > 1 else []
                try:
                    df = pd.DataFrame(body, columns=headers)
                except Exception:
                    df = pd.DataFrame(raw_table)
                tables.append(df)
    return tables


__all__ = ["extract_tables_to_dataframes"]
