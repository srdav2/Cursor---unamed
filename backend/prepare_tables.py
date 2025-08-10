import json
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd

from collector import update_index
from scraper import extract_financial_data, FINANCIAL_SCHEMA, BANK_REGISTRY

START_YEAR = 2020
END_YEAR = 2024

OUT_DIR = Path("data/standardized")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def build_rows() -> List[Dict[str, Any]]:
    idx = update_index()
    rows: List[Dict[str, Any]] = []

    for bank_code, meta in idx.items():
        bank_info = BANK_REGISTRY.get(bank_code.lower(), {})
        bank_name = bank_info.get("name")
        country = bank_info.get("country")
        reporting_currency = bank_info.get("reporting_currency")

        for r in meta.get("reports", []):
            try:
                year = int(r.get("year"))
            except Exception:
                continue
            if not (START_YEAR <= year <= END_YEAR):
                continue

            abs_path = r.get("abs_path") or r.get("path")
            if not abs_path:
                continue
            pdf_path = Path(abs_path).resolve()
            if not pdf_path.exists():
                continue

            extracted = extract_financial_data(pdf_path=pdf_path, schema=FINANCIAL_SCHEMA, bank=bank_code, year=year)

            # Construct a wide row of standardized metrics
            row: Dict[str, Any] = {
                "bank_code": bank_code,
                "bank_name": bank_name,
                "country": country,
                "reporting_currency_registry": reporting_currency,
                "year": year,
            }

            # Keep provenance in a nested dict
            provenance: Dict[str, Any] = {}

            for item in extracted:
                metric = item.get("metric_name")
                if not metric:
                    continue
                # Only set first hit for each metric
                if metric not in row:
                    row[metric] = item.get("value")
                    row[f"{metric}__raw"] = item.get("raw_value")
                    row[f"{metric}__units"] = item.get("value_units")
                    row[f"{metric}__currency_detected"] = item.get("value_currency")
                    provenance[metric] = {
                        "page": item.get("source_page"),
                        "term": item.get("source_term_used"),
                        "coords": item.get("source_coordinates"),
                        "snippet": item.get("snippet_path"),
                    }

            row["provenance"] = provenance
            rows.append(row)

    return rows


def main() -> None:
    rows = build_rows()

    # Save JSON
    json_path = OUT_DIR / "financials_2020_2024.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    # Save CSV (flatten provenance omitted in CSV)
    # Ensure all columns from schema are present
    schema_cols = [m["standard_name"] for m in FINANCIAL_SCHEMA]
    base_cols = ["bank_code", "bank_name", "country", "reporting_currency_registry", "year"]

    # Generate DataFrame
    df = pd.DataFrame(rows)

    # Ensure columns exist
    for col in schema_cols:
        if col not in df.columns:
            df[col] = pd.NA
        # Keep units and currency columns too
        ucol = f"{col}__units"
        ccol = f"{col}__currency_detected"
        rcol = f"{col}__raw"
        if ucol not in df.columns:
            df[ucol] = pd.NA
        if ccol not in df.columns:
            df[ccol] = pd.NA
        if rcol not in df.columns:
            df[rcol] = pd.NA

    ordered_cols = base_cols + sum([[c, f"{c}__raw", f"{c}__units", f"{c}__currency_detected"] for c in schema_cols], [])
    # Keep only ordered cols that exist
    ordered_cols = [c for c in ordered_cols if c in df.columns]
    df = df[ordered_cols]

    csv_path = OUT_DIR / "financials_2020_2024.csv"
    df.to_csv(csv_path, index=False)

    print(f"Wrote {json_path} and {csv_path}")


if __name__ == "__main__":
    main()