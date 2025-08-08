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


def main() -> None:
    """Temporary entry point used to verify the project skeleton runs."""
    print("Project skeleton ready. Next: implement scrapers, processors, and dashboard.")


if __name__ == "__main__":
    main()
