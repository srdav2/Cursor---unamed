import json
import os
from pathlib import Path
from typing import List, Dict, Any

from collector import collect_all, update_index
from scraper import FINANCIAL_SCHEMA, extract_financial_data


BANKS: List[str] = [
    # Australia
    "cba", "nab", "wbc", "anz", "mqg",
    # Canada
    "rbc", "td", "bns", "bmo", "cm", "nbc",
    # United States
    "jpm", "bac", "wfc", "c", "gs", "ms",
    # United Kingdom
    "hsbc", "barc", "lloy", "nwg", "stan",
    # Eurozone
    "bnpp", "aca", "san", "ing", "dbk", "isp",
    # Switzerland
    "ubs", "cs",
    # Japan
    "mufg", "smfg", "mizuho",
    # China
    "icbc", "ccb", "abc", "boc",
    # Singapore
    "dbs", "ocbc", "uob",
]

START_YEAR = 2020
END_YEAR = 2024

OUTPUT_DIR = Path("data/metrics")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_collection() -> None:
    # Collect up to the required range by asking for 6 years, then we will filter 2020-2024
    collect_all(BANKS, years=6)
    update_index()


def _iter_report_pdfs() -> List[Dict[str, Any]]:
    idx = update_index()
    items: List[Dict[str, Any]] = []
    for bank, meta in idx.items():
        for r in meta.get("reports", []):
            try:
                y = int(r.get("year"))
            except Exception:
                continue
            if START_YEAR <= y <= END_YEAR:
                items.append({"bank": bank, "year": y, "path": r.get("abs_path") or r.get("path")})
    # Ensure absolute paths
    for it in items:
        p = Path(it["path"]).resolve()
        it["path"] = str(p)
    return items


def extract_all() -> List[Dict[str, Any]]:
    items = _iter_report_pdfs()
    results: List[Dict[str, Any]] = []
    for it in items:
        pdf_path = Path(it["path"]) if it["path"] else None
        if not pdf_path or not pdf_path.exists():
            continue
        data = extract_financial_data(pdf_path=pdf_path, schema=FINANCIAL_SCHEMA, bank=it["bank"], year=it["year"])
        for row in data:
            results.append(row)
    return results


def save_outputs(rows: List[Dict[str, Any]]) -> None:
    # Save per-bank JSON and a combined CSV
    # Combined JSON
    combined_path = OUTPUT_DIR / "combined_2020_2024.json"
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    # Combined CSV
    import pandas as pd
    df = pd.DataFrame(rows)
    csv_path = OUTPUT_DIR / "combined_2020_2024.csv"
    df.to_csv(csv_path, index=False)

    # Group by bank for individual JSON files
    by_bank: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        by_bank.setdefault(r.get("bank_name") or "unknown", []).append(r)
    for bank, items in by_bank.items():
        with open(OUTPUT_DIR / f"{bank}_2020_2024.json", "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    run_collection()
    rows = extract_all()
    save_outputs(rows)
    print("Done. Outputs in data/metrics")
