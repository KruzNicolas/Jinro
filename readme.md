# Jinro - URL Shortener

Jinro is a robust and efficient URL shortening service designed for performance and scalability. It features secure API key management, rate limiting, and a clean RESTful API.

## Features

- 🔗 **URL Shortening**: Convert long URLs into compact, shareable links.
- 🔀 **Redirection**: Fast redirection to original URLs.
- 🔑 **Secure Authentication**: API Key-based access control with SHA-256 hashing.
- 🛡️ **Rate Limiting**: Built-in protection against abuse (SlowAPI).
- 🗑️ **Soft Delete**: Deactivate links without losing data history.
- 📊 **Database Integration**: Persistent storage using PostgreSQL and SQLModel.

## Tech Stack

- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Rate Limiting**: SlowAPI

## Getting Started

### Prerequisites

- Python 3.10 or higher
- PostgreSQL installed and running

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/KruzNicolas/Jinro.git
   cd Jinro
   ```

2. **Set up a Virtual Environment**

   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate it (Linux/macOS)
   source venv/bin/activate

   # Activate it (Windows)
   venv\Scripts\activate
   ```

3. **Install Dependencies**
   Navigate to the backend directory and install requirements:

   ```bash
   cd backend/shortener
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in `backend/shortener/` and add your database URL:
   ```env
   POSTGRE_URL=postgresql://user:password@localhost:5432/jinro_db
   ```

### Running the Application

Start the development server using FastAPI CLI or Uvicorn:

```bash
fastapi dev app/main.py
# OR
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Documentation

Detailed documentation is available in the `docs/` directory:

- [System Architecture](docs/architecture.md) - Overview of the system design and data flow.
- [API Reference](docs/api_reference.md) - Detailed guide to API endpoints.
- [Configuration](docs/configuration.md) - Environment variables setup.
- [Testing Guide](docs/testing.md) - How to run automated tests.
- [Troubleshooting](docs/troubleshooting.md) - Solutions for common issues.

## Usage

### Creating your first API Key

If the database is fresh, you can generate your first API key without authentication:

```bash
curl -X POST "http://localhost:8000/links/apikey" \
     -H "Content-Type: application/json" \
     -d '{"api_key": "my-secret-key"}'
```

### Creating a Short Link

Use the generated key to create a link:

```bash
curl -X POST "http://localhost:8000/links" \
     -H "Content-Type: application/json" \
     -d '{
           "api_key": "my-secret-key",
           "original_url": "https://www.google.com"
         }'
```

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

## License

Distributed under the MIT License. See `LICENSE` for more information.
