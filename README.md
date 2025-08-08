# Financial Analysis Web Application (Skeleton)

## Quickstart

1) Install deps

```
make install
```

2) Run a smoke check

```
python3 -m app.main --help
```

3) Run the dashboard

```
make run-app
# or
python3 -m app.main dash --host 0.0.0.0 --port 8050 --debug
```

4) Scrape a page with PDF links

```
make scrape URL=https://example.com OUTDIR=/workspace/data TIMEOUT=20
```

5) Process a downloaded PDF

```
make process PDF=/workspace/data/your.pdf OUT=/workspace/data/processed
```

## Structure
- `app/scrapers`: find and download PDFs
- `app/processors`: extract tables from PDFs to DataFrames
- `app/dashboards`: Dash layout and server
- `data`: PDFs and processed outputs

## Next
- Choose a real target website with PDF financials
- Add extraction rules for target bank PDF formats
- Persist cleaned data to SQLite/CSV
- Replace dummy dashboard data with live data from the DB/CSV
