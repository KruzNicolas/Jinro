# Troubleshooting Guide

## Common Issues

### 1. Database Connection Errors

**Error**: `ValueError: No DATABASE_URL set for the application.`

- **Cause**: The environment variable `POSTGRE_URL` is missing.
- **Solution**: Ensure you have a `.env` file in the `backend/shortener` directory with the correct connection string:
  ```env
  POSTGRE_URL=postgresql://user:password@localhost:5432/jinro_db
  ```

**Error**: `sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server... failed`

- **Cause**: The PostgreSQL server is not running or the connection details are incorrect.
- **Solution**:
  - Check if your Postgres service is active (`sudo systemctl status postgresql` on Linux).
  - Verify the host, port, user, and password in your `.env` file.

### 2. API Key Issues

**Error**: `401 Unauthorized: Invalid old API key.`

- **Cause**: You are trying to rotate the API key but provided an incorrect `old_api_key`.
- **Solution**: Verify you are using the correct current API key. If you have lost the key, you may need to manually reset the hash in the database or clear the `apikey` table (in development).

**Error**: `400 Bad Request: Unauthorized. API key already exists.`

- **Cause**: You tried to generate a new key without providing `old_api_key`, but the system already has a key registered.
- **Solution**: Provide the `old_api_key` in the request body to authorize the rotation.

### 3. Rate Limiting

**Error**: `429 Too Many Requests`

- **Cause**: You have exceeded the rate limit for the redirection endpoint (25 requests per minute).
- **Solution**: Wait for a minute before making more requests. This is a security feature to prevent abuse.

### 4. Import Errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'` (or other modules)

- **Cause**: Dependencies are not installed in the current environment.
- **Solution**:
  1. Activate your virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows).
  2. Install requirements: `pip install -r requirements.txt`.

## Logging

The application logs important events to the console and/or log files (configured in `logging_config.py`). Check the logs for detailed error messages and stack traces when debugging.
