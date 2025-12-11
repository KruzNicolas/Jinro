# Testing Guide

Jinro uses `pytest` for running automated tests. The tests use an in-memory SQLite database to ensure isolation and speed, so you don't need a running PostgreSQL instance to run them.

## Prerequisites

Ensure you have installed the test dependencies:

```bash
pip install -r backend/shortener/requirements.txt
```

This will install `pytest` and `httpx`.

## Running Tests

Navigate to the `backend/shortener` directory and run `pytest`:

```bash
cd backend/shortener
pytest
```

### Common Options

- **Verbose output**: See individual test results.

  ```bash
  pytest -v
  ```

- **Stop on first failure**:

  ```bash
  pytest -x
  ```

- **Run specific test file**:
  ```bash
  pytest tests/test_shortener_api.py
  ```

## Test Structure

Tests are located in `backend/shortener/tests/`.

- `conftest.py`: Contains fixtures for setting up the test database and FastAPI client.
- `test_shortener_api.py`: Contains the actual test cases for the API endpoints.

## What is tested?

- **Link Creation**: Verifies that links are created correctly with valid API keys.
- **Redirection**: Checks if short URLs correctly redirect to original URLs.
- **Authentication**: Ensures endpoints are protected and reject invalid keys.
- **Link Deletion**: Verifies soft delete functionality.
- **API Key Management**: Tests key generation and rotation logic.
