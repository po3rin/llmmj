# GitHub Actions Configuration

This repository uses GitHub Actions for continuous integration and testing with UV package manager.

## Workflows

### 1. Tests (`test.yml`)
![Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Tests/badge.svg)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**
- **test**: Main test suite with coverage reporting
- **test-generator**: Specific tests for generator module
- **test-evaluator**: Specific tests for evaluator module
- **test-integration**: Integration tests combining all modules

**Features:**
- ✅ Linting with Ruff
- ✅ Code formatting check
- ✅ Comprehensive test coverage
- ✅ Coverage reporting to Codecov
- ✅ Module-specific testing
- ✅ Import validation

### 2. PR Check (`pr-check.yml`)
![PR Check](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/PR%20Check/badge.svg)

**Triggers:**
- Pull requests to `main` or `develop` branches

**Jobs:**
- **quick-check**: Fast syntax and basic tests
- **changed-files**: Smart testing based on changed files

**Features:**
- 🚀 Fast feedback for pull requests
- 📁 Targeted testing based on changed files
- 🔍 Syntax validation
- 📦 Import verification

### 3. Nightly Tests (`nightly.yml`)
![Nightly Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Nightly%20Tests/badge.svg)

**Triggers:**
- Scheduled: Daily at 2 AM UTC
- Manual dispatch

**Jobs:**
- **comprehensive-test**: Full test suite with detailed reporting
- **dependency-check**: Dependency updates and security checks
- **lint-comprehensive**: Comprehensive code analysis
- **notify-on-failure**: Failure notifications

**Features:**
- 🌙 Daily comprehensive testing
- 📊 Detailed test reports
- 🔒 Security checks
- 📈 Code complexity analysis
- 🚨 Failure notifications

## UV Configuration

All workflows use [UV](https://docs.astral.sh/uv/) for fast Python package management:

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v3

- name: Set up Python 3.12
  run: uv python install 3.12

- name: Install dependencies
  run: uv sync --dev
```

## Test Configuration

Tests are configured in `pyproject.toml` with the following features:

- **Coverage**: Automatic coverage reporting
- **Markers**: Custom test markers for categorization
- **Async**: Support for async testing
- **HTML Reports**: Detailed HTML test reports

## Running Tests Locally

### Prerequisites
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --dev
```

### Run Tests
```bash
# All tests
uv run python -m pytest

# Specific modules
uv run python tests/run_tests.py generator
uv run python tests/run_tests.py evaluator

# With coverage
uv run python -m pytest --cov=. --cov-report=html

# Fast checks (like PR check)
uv run ruff check .
uv run ruff format --check .
```

## Badge URLs

To add badges to your main README.md, use these URLs (replace `YOUR_USERNAME` and `YOUR_REPO`):

```markdown
![Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Tests/badge.svg)
![PR Check](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/PR%20Check/badge.svg)
![Nightly Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Nightly%20Tests/badge.svg)
```

## Secrets Configuration

The following secrets may be needed:

- `CODECOV_TOKEN`: For coverage reporting (optional)
- Add notification tokens for Slack/Discord if using notifications

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are in `pyproject.toml`
2. **Coverage Issues**: Check `[tool.coverage.run]` configuration
3. **Linting Failures**: Run `uv run ruff check . --fix` locally
4. **Test Failures**: Run tests locally with `uv run python -m pytest -v`

### Debug Mode

To debug workflows locally:

```bash
# Install act (GitHub Actions local runner)
# Run specific workflow
act -j test

# Run with debug output
act -j test --verbose
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run tests locally: `uv run python -m pytest`
5. Run linting: `uv run ruff check . --fix`
6. Create a pull request

The PR Check workflow will automatically run and provide fast feedback on your changes.