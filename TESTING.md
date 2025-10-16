# Testing Guide

This project has multiple categories of tests.

## Test Categories

### Unit Tests

Fast tests that use mocks and don't require external resources.

```bash
# Run all tests except E2E
pytest tests/ -m "not e2e"
```

### End-to-End (E2E) Tests

Slower tests that make real HTTP requests to test the full integration flow.

```bash
# Run only E2E tests
pytest tests/test_e2e.py -m e2e -v

# Or run specific E2E test
pytest tests/test_e2e.py::test_download_json_e2e -v
```

### All Tests

```bash
# Run all tests including E2E
pytest tests/ -v
```

## Coverage

Check test coverage:

```bash
# Coverage excluding E2E tests (fast)
pytest tests/ -m "not e2e" --cov=src/azip --cov-report=term-missing

# Full coverage including E2E tests (slow)
pytest tests/ --cov=src/azip --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=src/azip --cov-report=html
open htmlcov/index.html
```

## Test Structure

```log
tests/
├── test_cli.py         # CLI command tests (mocked)
├── test_downloader.py  # Downloader unit tests (mocked with BeautifulSoup)
├── test_main.py        # Main entry point tests
└── test_e2e.py         # End-to-end integration tests (real HTTP requests)
```

## Prerequisites for E2E Tests

E2E tests make real HTTP requests to Microsoft's download page. No special setup is required, but:

- Tests may be slow (network dependent)
- Tests may fail if the service is unavailable
- Consider running them separately from unit tests in CI/CD

## Continuous Integration

For CI/CD pipelines, you may want to:

1. Run unit tests on every commit (fast feedback)
2. Run E2E tests on pull requests or main branch (thorough validation)

Example GitHub Actions workflow:

```yaml
# Fast unit tests on every push
- name: Run unit tests
  run: pytest tests/ -m "not e2e" --cov=src/azip

# E2E tests only on main branch or PRs
- name: Run E2E tests
  if: github.ref == 'refs/heads/main' || github.event_name == 'pull_request'
  run: pytest tests/test_e2e.py -m e2e -v
```

## Writing New Tests

### Unit Test Example

```python
def test_my_function(monkeypatch):
    # Use mocks for external dependencies
    monkeypatch.setattr("module.function", fake_function)
    result = my_function()
    assert result == expected
```

### E2E Test Example

```python
@pytest.mark.e2e
def test_real_download(tmp_path):
    # Makes real HTTP request, no mocks
    result = download_json(
        destination=tmp_path / "output.json",
        timeout_s=30,
    )
    assert result.exists()
```
