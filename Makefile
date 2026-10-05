PYTHON ?= python3
PYTHONPATH := src

.PHONY: test docs-check

test:
	PYTHONPATH=$(PYTHONPATH) pytest tests/ -v

docs-check:
	$(PYTHON) scripts/check_docs_consistency.py
