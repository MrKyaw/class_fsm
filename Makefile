.PHONY: install test coverage check cli clean

install:
	python -m pip install -e ".[dev]"

test:
	pytest

coverage:
	pytest --cov=fsm_kit --cov-report=term-missing --cov-report=html

check: coverage

cli:
	python -m fsm_kit 1101

clean:
	rm -rf .pytest_cache .coverage htmlcov coverage.xml build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
