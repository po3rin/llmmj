.PHONY: help format lint check install clean

# Default target
help:
	@echo "Available targets:"
	@echo "  format  - Format code with isort and ruff"
	@echo "  lint    - Lint code with ruff"
	@echo "  check   - Check code formatting and linting"
	@echo "  install - Install dependencies"
	@echo "  clean   - Clean cache and temporary files"

# Format code
format:
	@echo "Running isort..."
	uv run --group dev isort .
	@echo "Running ruff format..."
	uv run --group dev ruff format .
	@echo "Code formatting completed!"

# Lint code
lint:
	@echo "Running ruff check..."
	uv run --group dev ruff check .

# Check code (lint + format check)
check:
	@echo "Checking code formatting..."
	uv run --group dev isort --check-only .
	uv run --group dev ruff format --check .
	@echo "Running linter..."
	uv run --group dev ruff check .
	@echo "All checks passed!"

# Install dependencies
install:
	uv sync --all-groups

# Clean cache and temporary files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cache files cleaned!"