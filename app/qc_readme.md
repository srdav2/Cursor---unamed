# QC Pipeline & Dashboard

- Put PDFs under `data/pdfs/`.
- Install deps (example): `pip install -r requirements.txt` plus system deps for PyMuPDF.
- Run pipeline: `python -m app.main`
- Run pipeline + dashboard: `python -m app.main --serve`

Screenshots are saved under `data/screenshots/<pdf-stem>/` and linked in the dashboard. Use the Validated column to tick human-checked rows.