.PHONY: install run build lint publish-check

install:
	uv sync

run:
	uv run database

build:
	uv build

lint:
	uv run ruff check .

publish-check: build
	uvx twine check dist/*