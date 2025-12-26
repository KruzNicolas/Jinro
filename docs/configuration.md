# Configuration Guide

This guide details the environment variables required to run the Jinro application.

## Environment Variables

Create a `.env` file in the `backend/shortener/` directory based on the provided `.env.example`.

### 1. Database Configuration (`POSTGRE_URL`)

**Required**

The connection string for the PostgreSQL database.

- **Format**: `postgresql://<username>:<password>@<host>:<port>/<database_name>`
- **Example**: `postgresql://postgres:mysecretpassword@localhost:5432/jinro`

| Component       | Description                                                       |
| --------------- | ----------------------------------------------------------------- |
| `username`      | Your PostgreSQL username (e.g., `postgres`)                       |
| `password`      | Your PostgreSQL password                                          |
| `host`          | Database host address (e.g., `localhost` or `db` if using Docker) |
| `port`          | PostgreSQL port (default is `5432`)                               |
| `database_name` | Name of the database to use                                       |

### 2. Metrics Service (`METRICS_SERVICE_URL`)

**Optional**

The URL for the external metrics service, if you are using one to track usage statistics.

- **Default**: `None` (if not set)
- **Example**: `http://metrics-service:9090`

## Setup Instructions

1. Copy the example file:

   ```bash
   cp backend/shortener/.env.example backend/shortener/.env
   ```

2. Edit the `.env` file with your actual configuration values.
