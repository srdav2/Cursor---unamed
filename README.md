# Bank Financials Comparator (MVP)

Python-based system to ingest PDF financial statements, extract key metrics with provenance, and visualize across banks with a QC workflow.

## Stack
- Backend: FastAPI
- Frontend (MVP): Streamlit
- Planned services: Postgres, Redis, MinIO, Celery workers

## Quick start (local)

1) Python environment
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2) Run API (dev)
```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
Health check: `http://localhost:8000/api/health`

3) Run Streamlit (MVP)
```bash
streamlit run frontend/streamlit_app/Home.py
```

## Next
- Implement file upload, storage, and page rendering
- Add extraction pipeline for MVP metrics (NII, NIM, Total loans, CET1, NPL ratio)
- QC workflow with provenance (page, bbox, confidence)
- Dashboards for single and multi-bank comparison
