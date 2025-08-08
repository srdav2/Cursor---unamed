"""
Financial Analysis Web Application (with QC pipeline)

- Run QC pipeline to parse PDFs under data/pdfs, render screenshots, and
  persist extracted items to SQLite.
- Optionally start the Dash QC dashboard.

Usage:
  python -m app.main            # run pipeline only
  python -m app.main --serve    # run pipeline then start dashboard
"""
from __future__ import annotations

import argparse

from .qc_pipeline import run_qc_pipeline
from .dashboards.app import create_app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true", help="Start QC dashboard after pipeline")
    parser.add_argument("--pdf-dir", type=str, default=None, help="Override PDF directory")
    args = parser.parse_args()

    inserted = run_qc_pipeline(args.pdf_dir)
    print(f"QC pipeline complete. Inserted/updated rows: {inserted}")

    if args.serve:
        app = create_app()
        app.run_server(debug=True)


if __name__ == "__main__":
    main()
