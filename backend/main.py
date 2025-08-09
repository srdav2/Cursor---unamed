from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from pathlib import Path

from scraper import extract_financial_data, FINANCIAL_SCHEMA, BANK_REGISTRY
from collector import collect_bank_reports, collect_all, collect_from_urls, update_index, cleanup_reports, migrate_existing, load_bank_sources

# Import AI classifier
try:
    from ai_classifier import classify_document, classify_batch, get_classifier
    AI_CLASSIFIER_AVAILABLE = True
except ImportError:
    AI_CLASSIFIER_AVAILABLE = False

app = Flask(__name__)
# Relaxed CORS for file:// origin (shows as Origin: null)
CORS(app, resources={r"/api/*": {"origins": ["*", "null"]}}, supports_credentials=False)

@app.route('/api/status')
def status():
    return {"status": "Backend is running!"}


@app.route('/api/extract')
def api_extract():
    """
    Extracts schema-based metrics from a PDF.
    Usage examples:
    - /api/extract?pdf=data/downloads/NAB_FY24_Annual_Report.pdf&bank=nab&year=2024
    - /api/extract?pdf=/absolute/path/to/report.pdf
    """
    pdf = request.args.get('pdf')
    bank = request.args.get('bank')
    year_str = request.args.get('year')
    year = int(year_str) if year_str and year_str.isdigit() else None

    if not pdf:
        return jsonify({"error": "Missing required query param 'pdf'"}), 400

    pdf_path = Path(pdf)
    if not pdf_path.exists():
        return jsonify({"error": f"PDF not found at {pdf_path}"}), 404

    data = extract_financial_data(pdf_path=pdf_path, schema=FINANCIAL_SCHEMA, bank=bank, year=year)
    return jsonify({
        "bank": bank,
        "year": year,
        "source_pdf": str(pdf_path),
        "items": data,
    })


@app.route('/api/collect', methods=['POST'])
def api_collect():
    """
    Trigger download/discovery of up to 6 years of annual reports for a bank.
    JSON body: { "bank": "nab", "years": 6 }
    """
    body = request.get_json(silent=True) or {}
    bank = (body.get('bank') or '').strip().lower()
    years = int(body.get('years') or 6)
    if not bank:
        return jsonify({"error": "Missing 'bank' in request body"}), 400
    result = collect_bank_reports(bank, years=years)
    update_index()
    return jsonify({"bank": bank, **result})


@app.route('/api/collect_all', methods=['POST'])
def api_collect_all():
    """
    Trigger download/discovery for a list of banks.
    JSON body: { "banks": ["cba","nab",...], "years": 6 }
    """
    body = request.get_json(silent=True) or {}
    banks = body.get('banks') or []
    years = int(body.get('years') or 6)
    if not isinstance(banks, list) or not banks:
        return jsonify({"error": "Provide non-empty 'banks' array in body"}), 400
    result = collect_all([b.lower() for b in banks], years=years)
    update_index()
    return jsonify(result)


@app.route('/api/index')
def api_index():
    idx = update_index()
    return jsonify(idx)


@app.route('/api/index/approve', methods=['POST'])
def api_index_approve():
    body = request.get_json(silent=True) or {}
    bank = (body.get('bank') or '').lower().strip()
    year = str(body.get('year') or '').strip()
    if not bank or not year:
        return jsonify({"error": "bank and year required"}), 400
    # create approval file marker next to PDF
    from collector import update_index
    idx = update_index()
    entry = next((r for r in idx.get(bank, {}).get('reports', []) if r['year'] == year), None)
    if not entry:
        return jsonify({"error": "entry not found"}), 404
    # Construct absolute path from relative path
    abs_path = Path(entry['path']).resolve()
    marker = str(abs_path) + '.approved'
    import os
    try:
        with open(marker, 'w') as f:
            f.write('approved')
    except OSError:
        return jsonify({"error": "failed to write approval"}), 500
    return jsonify({"ok": True})


@app.route('/api/index/reject', methods=['POST'])
def api_index_reject():
    body = request.get_json(silent=True) or {}
    bank = (body.get('bank') or '').lower().strip()
    year = str(body.get('year') or '').strip()
    if not bank or not year:
        return jsonify({"error": "bank and year required"}), 400
    from collector import update_index
    idx = update_index()
    entry = next((r for r in idx.get(bank, {}).get('reports', []) if r['year'] == year), None)
    if not entry:
        return jsonify({"error": "entry not found"}), 404
    # Construct absolute path from relative path
    abs_path = Path(entry['path']).resolve()
    # remove the file
    import os
    try:
        if os.path.exists(abs_path):
            os.remove(abs_path)
        # remove marker if exists
        if os.path.exists(str(abs_path) + '.approved'):
            os.remove(str(abs_path) + '.approved')
    except OSError:
        return jsonify({"error": "failed to delete"}), 500
    update_index()
    return jsonify({"ok": True})


@app.route('/api/file')
def api_file():
    """Serve a stored PDF by bank/year so the browser can open it, even when the UI runs from file://"""
    bank = (request.args.get('bank') or '').lower().strip()
    year = str(request.args.get('year') or '').strip()
    if not bank or not year:
        return jsonify({"error": "bank and year required"}), 400
    idx = update_index()
    entry = next((r for r in idx.get(bank, {}).get('reports', []) if r['year'] == year), None)
    if not entry:
        return jsonify({"error": "entry not found"}), 404
    try:
        # Construct absolute path from relative path
        abs_path = Path(entry['path']).resolve()
        return send_file(abs_path, as_attachment=False)
    except Exception as exc:
        return jsonify({"error": f"failed to open file: {exc}"}), 500


@app.route('/api/collect_from_urls', methods=['POST'])
def api_collect_from_urls():
    """
    Manually ingest reports from provided URLs or local file paths.
    Body: { "bank": "nab", "items": [{"year":"2024","url":"/abs/path.pdf"}, ...] }
    """
    body = request.get_json(silent=True) or {}
    bank = (body.get('bank') or '').strip().lower()
    items = body.get('items') or []
    if not bank or not isinstance(items, list) or not items:
        return jsonify({"error": "Provide 'bank' and non-empty 'items' array"}), 400
    result = collect_from_urls(bank, items)
    return jsonify({"bank": bank, **result})


@app.route('/api/banks')
def api_banks():
    """Return known bank codes and metadata for UI selection."""
    items = []
    for code, meta in BANK_REGISTRY.items():
        items.append({"code": code, **meta})
    items.sort(key=lambda x: x["code"]) 
    sources = load_bank_sources()
    return jsonify({"banks": items, "sources": sources})


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """
    Accepts a file upload with form fields: bank, year, file
    Saves to standardized path and updates index.
    """
    if 'file' not in request.files:
        return jsonify({"error": "Missing file"}), 400
    file = request.files['file']
    bank = (request.form.get('bank') or '').strip().lower()
    year_str = (request.form.get('year') or '').strip()
    if not bank or not year_str:
        return jsonify({"error": "Missing bank or year"}), 400
    try:
        year = int(year_str)
    except Exception:
        return jsonify({"error": "Invalid year"}), 400

    from collector import build_report_path
    dest = build_report_path(bank, year)
    import os
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    file.save(dest)
    update_index()
    return jsonify({"bank": bank, "year": year, "path": dest})


@app.route('/api/maintenance/cleanup', methods=['POST', 'GET'])
def api_cleanup():
    return jsonify(cleanup_reports())


@app.route('/api/maintenance/migrate', methods=['POST', 'GET'])
def api_migrate():
    """Migrate existing reports to new structure."""
    result = migrate_existing()
    return jsonify(result)


@app.route('/api/ai/classify', methods=['POST'])
def api_ai_classify():
    """
    AI-powered document classification endpoint.
    JSON body: { "pdf_path": "/path/to/document.pdf" }
    """
    if not AI_CLASSIFIER_AVAILABLE:
        return jsonify({"error": "AI classifier not available"}), 503
    
    body = request.get_json(silent=True) or {}
    pdf_path = body.get('pdf_path', '').strip()
    
    if not pdf_path:
        return jsonify({"error": "Missing 'pdf_path' in request body"}), 400
    
    if not Path(pdf_path).exists():
        return jsonify({"error": f"PDF not found at {pdf_path}"}), 404
    
    try:
        result = classify_document(pdf_path)
        return jsonify({
            "pdf_path": pdf_path,
            "ai_available": True,
            **result
        })
    except Exception as e:
        return jsonify({"error": f"Classification failed: {str(e)}"}), 500


@app.route('/api/ai/classify_batch', methods=['POST'])
def api_ai_classify_batch():
    """
    AI-powered batch document classification endpoint.
    JSON body: { "pdf_paths": ["/path/to/doc1.pdf", "/path/to/doc2.pdf"] }
    """
    if not AI_CLASSIFIER_AVAILABLE:
        return jsonify({"error": "AI classifier not available"}), 503
    
    body = request.get_json(silent=True) or {}
    pdf_paths = body.get('pdf_paths', [])
    
    if not isinstance(pdf_paths, list) or not pdf_paths:
        return jsonify({"error": "Provide non-empty 'pdf_paths' array in body"}), 400
    
    # Validate all paths exist
    missing_paths = [p for p in pdf_paths if not Path(p).exists()]
    if missing_paths:
        return jsonify({"error": f"PDFs not found: {missing_paths}"}), 404
    
    try:
        results = classify_batch(pdf_paths)
        return jsonify({
            "ai_available": True,
            "results": results
        })
    except Exception as e:
        return jsonify({"error": f"Batch classification failed: {str(e)}"}), 500


@app.route('/api/ai/status')
def api_ai_status():
    """Check AI classifier status and availability."""
    status = {
        "ai_available": AI_CLASSIFIER_AVAILABLE,
        "model_loaded": False
    }
    
    if AI_CLASSIFIER_AVAILABLE:
        try:
            classifier = get_classifier()
            status["model_loaded"] = classifier.model is not None
            status["model_name"] = classifier.model_name
            status["device"] = classifier.device
        except Exception as e:
            status["error"] = str(e)
    
    return jsonify(status)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
