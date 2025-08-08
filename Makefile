.PHONY: install run-app run-main-help scrape process

install:
	pip3 install --no-input --break-system-packages -r requirements.txt

run-app:
	python3 -m app.dashboards.app

run-main-help:
	python3 -m app.main --help

# Usage: make scrape URL=https://example.com OUTDIR=/workspace/data TIMEOUT=20
scrape:
	python3 -m app.main scrape $(URL) --outdir $(or $(OUTDIR),/workspace/data) --timeout $(or $(TIMEOUT),20)

# Usage: make process PDF=/workspace/data/file.pdf OUT=/workspace/data/processed
process:
	python3 -m app.main process $(PDF) --output-dir $(or $(OUT),/workspace/data/processed)
