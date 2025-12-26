# API Reference

Base URL: `http://localhost:8000` (default)

## Authentication

Most write operations require an API Key. This should be passed in the request body as `api_key`.

## Endpoints

### 1. Shortener

#### Create a Short Link

Creates a new shortened URL.

- **URL**: `/links`
- **Method**: `POST`
- **Auth Required**: Yes
- **Body**:
  ```json
  {
    "api_key": "your_api_key",
    "original_url": "https://example.com/very/long/url",
    "short_url": "custom-alias" // Optional
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "id": "uuid-string",
    "original_url": "https://example.com/very/long/url",
    "short_url": "custom-alias",
    "is_active": true,
    "created_at": "2025-10-08T12:00:00Z"
  }
  ```

#### Get All Links

Retrieves a list of all shortened URLs.

- **URL**: `/links`
- **Method**: `GET`
- **Auth Required**: No (Public for now, subject to change)
- **Response** (200 OK):
  ```json
  [
    {
      "id": "uuid-string",
      "original_url": "...",
      "short_url": "...",
      "is_active": true,
      "created_at": "..."
    }
  ]
  ```

#### Delete (Deactivate) a Link

Soft deletes a link, making it inactive.

- **URL**: `/links/{short_url}`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **Body**:
  ```json
  {
    "api_key": "your_api_key"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "message": "Link deactivated successfully"
  }
  ```

#### Redirect to Original URL

Redirects the user to the original URL associated with the short code.

- **URL**: `/{short_url}`
- **Method**: `GET`
- **Rate Limit**: 25 requests / minute
- **Response**:
  - **307 Temporary Redirect**: If found.
  - **404 Not Found**: If the link does not exist or is inactive.

---

### 2. API Key Management

#### Generate/Rotate API Key

Generates a new API key. If an API key already exists, the old one must be provided for validation.

- **URL**: `/links/apikey`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "api_key": "new_desired_key",
    "old_api_key": "current_key" // Required if a key already exists
  }
  ```
- **Response** (200 OK):
  Returns the new API key string.

## Error Codes

- **400 Bad Request**: Invalid input or API key already exists (when trying to create initial key without need).
- **401 Unauthorized**: Invalid API key provided.
- **404 Not Found**: Resource not found.
- **429 Too Many Requests**: Rate limit exceeded.
