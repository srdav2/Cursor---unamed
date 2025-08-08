"""
Financial Analysis Web Application (Project Skeleton)

Purpose:
- Download PDF financial statements from bank websites.
- Extract key financial data from the PDFs.
- Store and transform the data for analysis.
- Visualize the results in an interactive web dashboard.

Core Technologies:
- requests, BeautifulSoup (web scraping)
- pdfplumber (PDF data extraction)
- pandas (data manipulation)
- Dash (web dashboard)
- SQLite (lightweight database)

Structure:
- app/                → Application code
  - scrapers/         → Scripts to download PDFs from bank websites
  - processors/       → Scripts to extract and clean data from PDFs
  - dashboards/       → Dash app layout, callbacks, and UI logic
- data/               → Downloaded PDFs, processed CSVs, and local SQLite DB

How you'll use this file later:
- This file will become the orchestrator. It will call functions from scrapers to download PDFs, processors to parse them into tables, save data to SQLite/CSV, and then start the Dash server.
- For now, it just prints a message so you can test the environment with:  python -m app.main
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.scrapers.bank_scraper import download_pdfs
from app.processors.pdf_processor import extract_tables_to_dataframes
from app.dashboards.app import create_app


def command_scrape(args: argparse.Namespace) -> None:
    results = download_pdfs(args.url, args.outdir, timeout_seconds=args.timeout)
    ok = sum(1 for r in results if r.ok)
    failed = len(results) - ok
    print(f"Scrape complete: {ok} succeeded, {failed} failed.")
    for r in results:
        status = "OK" if r.ok else f"FAIL ({r.status_code or r.error})"
        print(f"- {status}: {r.url} -> {r.output_path}")


def command_process(args: argparse.Namespace) -> None:
    pdf_path = args.pdf
    if not Path(pdf_path).exists():
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    dataframes = extract_tables_to_dataframes(pdf_path)
    if not dataframes:
        print("No tables detected in the PDF.")
        return
    print(f"Extracted {len(dataframes)} table(s):")
    output_dir: Path | None = Path(args.output_dir) if args.output_dir else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
    for index, df in enumerate(dataframes, start=1):
        shape = "x".join(map(str, df.shape))
        print(f"- Table {index}: shape {shape}")
        if output_dir:
            out_csv = output_dir / f"table_{index}.csv"
            df.to_csv(out_csv, index=False)
            print(f"  saved -> {out_csv}")


def command_dash(args: argparse.Namespace) -> None:
    app = create_app()
    app.run_server(debug=args.debug, host=args.host, port=args.port)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Financial Analysis App CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_scrape = sub.add_parser("scrape", help="Discover and download PDFs from a page")
    p_scrape.add_argument("url", help="Starting URL that links to PDFs")
    p_scrape.add_argument("--outdir", default=str(Path("/workspace/data"))),
    p_scrape.add_argument("--timeout", type=int, default=20)
    p_scrape.set_defaults(func=command_scrape)

    p_proc = sub.add_parser("process", help="Extract tables from a PDF to CSVs")
    p_proc.add_argument("pdf", help="Path to a PDF file")
    p_proc.add_argument("--output-dir", default=str(Path("/workspace/data/processed")))
    p_proc.set_defaults(func=command_process)

    p_dash = sub.add_parser("dash", help="Run the Dash dashboard server")
    p_dash.add_argument("--host", default="127.0.0.1")
    p_dash.add_argument("--port", type=int, default=8050)
    p_dash.add_argument("--debug", action="store_true")
    p_dash.set_defaults(func=command_dash)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
