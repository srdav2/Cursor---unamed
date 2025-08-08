"""
SQLite storage utilities for the financial analysis app.

Schema (initial):
- metrics(id INTEGER PRIMARY KEY, category TEXT, amount REAL, source TEXT, created_at TEXT)

This is a minimal starting point; we will expand with normalized tables later
(e.g., statements, accounts, line_items) as requirements become clearer.
"""
from __future__ import annotations

import os
import pathlib
import sqlite3
from typing import Iterable, Optional

import pandas as pd

DB_PATH_DEFAULT = str(pathlib.Path("data") / "app.db")


def ensure_parent_directory(file_path: str) -> None:
    pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)


def connect(db_path: Optional[str] = None) -> sqlite3.Connection:
    db_file = db_path or DB_PATH_DEFAULT
    ensure_parent_directory(db_file)
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            source TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()


def insert_metric(conn: sqlite3.Connection, category: str, amount: float, source: Optional[str] = None) -> int:
    cur = conn.execute(
        "INSERT INTO metrics(category, amount, source) VALUES (?, ?, ?)",
        (category, float(amount), source),
    )
    conn.commit()
    return int(cur.lastrowid)


def insert_metrics_bulk(conn: sqlite3.Connection, rows: Iterable[tuple[str, float, Optional[str]]]) -> None:
    conn.executemany(
        "INSERT INTO metrics(category, amount, source) VALUES (?, ?, ?)",
        [(c, float(a), s) for c, a, s in rows],
    )
    conn.commit()


def insert_metrics_dataframe(conn: sqlite3.Connection, df: pd.DataFrame) -> None:
    expected_cols = {"category", "amount"}
    if not expected_cols.issubset(df.columns):
        raise ValueError("DataFrame must include columns: 'category', 'amount' (optional 'source')")
    rows = [
        (
            str(row.get("category")),
            float(row.get("amount")),
            (None if pd.isna(row.get("source")) else str(row.get("source"))),
        )
        for _, row in df.iterrows()
    ]
    insert_metrics_bulk(conn, rows)


def fetch_metrics_dataframe(conn: sqlite3.Connection) -> pd.DataFrame:
    cur = conn.execute("SELECT id, category, amount, source, created_at FROM metrics ORDER BY id")
    rows = cur.fetchall()
    if not rows:
        return pd.DataFrame(columns=["id", "category", "amount", "source", "created_at"])
    return pd.DataFrame([dict(r) for r in rows])
