.PHONY: install run dev test lint format build clean

install:
	pip install -e ".[dev,ai]"

run:
	docpybara --dir ./docs --port 8000

dev:
	docpybara --dir ./docs --port 8000 --reload

test:
	python -m pytest tests/ -v

lint:
	ruff check src/ tests/

format:
	ruff check --fix src/ tests/

build:
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info src/*.egg-info
