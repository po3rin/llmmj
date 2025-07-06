# Makefile for llmmj project

.PHONY: help install test clean lint format setup

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean cache files"
	@echo "  make setup      - Initial setup"

install:
	uv sync

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov .ruff_cache

setup: install
	@echo "Setup complete!"