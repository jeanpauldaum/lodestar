.PHONY: install ingest analyze api test clean

install:
	pip install -e ".[dev]"

ingest:
	lodestar ingest

analyze:
	lodestar analyze --city "$(CITY)" --domain "$(DOMAIN)" $(if $(COUNTRY),--country "$(COUNTRY)",)

api:
	uvicorn lodestar.api.main:app --reload

test:
	pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
	find . -name "*.pyc" -delete 2>/dev/null; \
	rm -rf .chroma 2>/dev/null; \
	echo "Cleaned."
