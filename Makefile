.PHONY: help format lint check install clean test test-generator test-evaluator test-all ci-setup ci-check

# Default target
help:
	@echo "Available targets:"
	@echo "  format         - Format code with isort and ruff"
	@echo "  lint           - Lint code with ruff"
	@echo "  check          - Check code formatting and linting (same as GitHub Actions)"
	@echo "  test           - Run tests with pytest"
	@echo "  test-generator - Run generator tests only"
	@echo "  test-evaluator - Run evaluator tests only"
	@echo "  test-all       - Run all tests (same as GitHub Actions)"
	@echo "  ci-setup       - Setup environment like GitHub Actions"
	@echo "  ci-check       - Run all checks like GitHub Actions"
	@echo "  install        - Install dependencies"
	@echo "  clean          - Clean cache and temporary files"

# Setup environment like GitHub Actions
ci-setup:
	@echo "Setting up environment like GitHub Actions..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example"; fi
	@export PYTHONPATH=. && echo "PYTHONPATH set to current directory"
	uv sync --dev
	@echo "Environment setup completed!"

# Run all checks like GitHub Actions
ci-check: ci-setup
	@echo "Running all checks like GitHub Actions..."
	@echo "=== Environment Info ==="
	uv --version
	uv run python --version
	@echo "Working directory: $$(pwd)"
	@echo "PYTHONPATH: $$PYTHONPATH"
	@echo "=== Running Ruff linting ==="
	PYTHONPATH=. uv run ruff check . --output-format=github
	@echo "=== Running Ruff format check ==="
	PYTHONPATH=. uv run ruff format --check .
	@echo "=== Testing imports ==="
	PYTHONPATH=. uv run python -c "import entity.entity; print('✓ entity.entity import works')"
	PYTHONPATH=. uv run python -c "import exceptions.exceptions; print('✓ exceptions.exceptions import works')"
	@echo "=== Running pytest ==="
	PYTHONPATH=. uv run pytest -v
	@echo "All checks passed like GitHub Actions!"

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
	PYTHONPATH=. uv run --group dev ruff check .

# Check code (lint + format check) - GitHub Actions compatible
check:
	@echo "=== Running Ruff linting ==="
	PYTHONPATH=. uv run --group dev ruff check . --output-format=github
	@echo "=== Running Ruff format check ==="
	PYTHONPATH=. uv run --group dev ruff format --check .
	@echo "All checks passed!"

# Install dependencies
install:
	uv sync --dev

# Run tests - GitHub Actions compatible
test:
	@echo "=== Running pytest ==="
	PYTHONPATH=. uv run pytest -v

# Run generator tests only
test-generator:
	@echo "=== Running generator tests ==="
	PYTHONPATH=. uv run python tests/run_tests.py generator

# Run evaluator tests only
test-evaluator:
	@echo "=== Running evaluator tests ==="
	PYTHONPATH=. uv run python tests/run_tests.py evaluator

# Run all tests
test-all:
	@echo "=== Running all tests ==="
	PYTHONPATH=. uv run python tests/run_tests.py
	@echo "=== Testing imports ==="
	PYTHONPATH=. uv run python -c "from generator.generator import MahjongQuestionGenerator; print('Generator import successful')"
	PYTHONPATH=. uv run python -c "from evaluator.evaluator import MahjongEvaluator; print('Evaluator import successful')"

# Clean cache and temporary files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".uv-cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cache files cleaned!"