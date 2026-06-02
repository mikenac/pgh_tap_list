.PHONY: sync test lint scrape compare enrich report site-build run-local

sync:
	uv sync --group dev

test:
	uv run --group dev pytest

lint:
	uv run --group dev ruff check src tests

scrape:
	uv run --group dev python scripts/scrape.py

enrich:
	uv run --group dev python scripts/enrich_untappd.py

compare:
	uv run --group dev python scripts/compare.py

report:
	uv run --group dev python scripts/generate_report.py

site-build:
	npm run build

run-local:
	npm run dev -- --host 127.0.0.1 --port 4321
