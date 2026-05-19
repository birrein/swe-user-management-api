# SWE User Management API

RESTful user management API built with FastAPI, PostgreSQL, SQLAlchemy async, Alembic, Docker, Cloud Run, and Cloud Build.

This project solves the Software Engineer Challenge with a pragmatic Clean Architecture approach. FastAPI and SQLAlchemy are treated as adapters, while the application use cases depend on a `UserRepository` port. That keeps PostgreSQL replaceable without changing the HTTP API or business rules.

## Architecture

```text
HTTP request
  -> FastAPI router
  -> Pydantic schema
  -> application use case
  -> UserRepository port
  -> SQLAlchemy adapter
  -> PostgreSQL
```

```text
src/
  api/              FastAPI routes, schemas, dependencies
  application/      Use cases and repository ports
  domain/           User entity, roles, domain exceptions
  infrastructure/   SQLAlchemy models, sessions, repository adapters
alembic/            Versioned database migrations
tests/              API and use-case tests
```

## Features

- Versioned API under `/api/v1`
- CRUD operations for users
- Soft delete through `active=false`
- Pagination in `GET /users`
- Email, username, and role validation
- Unique constraints for `username` and `email`
- Alembic migrations
- JSON logs to stdout, compatible with Cloud Logging
- Docker and Docker Compose support
- Cloud Build pipeline for test, build, push, and Cloud Run deploy

## API

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Application health |
| `POST` | `/api/v1/users` | Create a user |
| `GET` | `/api/v1/users` | List users |
| `GET` | `/api/v1/users/{id}` | Get a user by id |
| `PATCH` | `/api/v1/users/{id}` | Update a user |
| `DELETE` | `/api/v1/users/{id}` | Soft delete a user |

Interactive OpenAPI documentation is available at `/docs`.

## Requirements

- Python 3.12
- Docker
- Docker Compose
- Google Cloud CLI for deployment
- A GCP project with billing enabled

## Local Setup

```bash
pyenv local 3.12.12
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
cp .env.example .env
```

Start PostgreSQL:

```bash
docker compose up -d db
```

Run migrations:

```bash
alembic upgrade head
```

Run the API:

```bash
uvicorn src.main:app --reload
```

Open:

```text
http://localhost:8000/docs
```

## Docker Compose

Run the API and PostgreSQL together:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8080/docs
```

## Tests

```bash
pytest
```

The default test suite uses an in-memory repository through FastAPI dependency overrides. This keeps CI deterministic while the production adapter remains PostgreSQL-backed.

## Postman

Import the files in `postman/` to test the API manually:

- `postman/swe-user-management-api.postman_collection.json`
- `postman/local.postman_environment.json`
- `postman/cloud-run.postman_environment.json`

The collection includes a full smoke CRUD flow, duplicate-user checks, and validation examples.

## Example Requests

Create a user:

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "manuel_marin",
    "email": "manuel.marin@example.com",
    "first_name": "Manuel",
    "last_name": "Marin",
    "role": "user",
    "active": true
  }'
```

List active users:

```bash
curl "http://localhost:8000/api/v1/users?skip=0&limit=50"
```

List inactive guests:

```bash
curl "http://localhost:8000/api/v1/users?active=false&role=guest"
```

Get a user:

```bash
curl http://localhost:8000/api/v1/users/{user_id}
```

Update a user:

```bash
curl -X PATCH http://localhost:8000/api/v1/users/{user_id} \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}'
```

Soft delete a user:

```bash
curl -X DELETE http://localhost:8000/api/v1/users/{user_id}
```

## Configuration

| Variable | Description | Example |
| --- | --- | --- |
| `ENVIRONMENT` | Runtime environment | `local` |
| `LOG_LEVEL` | Python log level | `INFO` |
| `DATABASE_URL` | Async SQLAlchemy PostgreSQL URL | `postgresql+asyncpg://user:pass@host:5432/db` |

For Cloud Run with Cloud SQL Unix sockets, store a secret named `swe-database-url` with a value like:

```text
postgresql+asyncpg://USER:PASSWORD@/DB_NAME?host=/cloudsql/PROJECT_ID:us-central1:swe-postgres
```

## GCP Deployment

Create the required GCP resources before running Cloud Build:

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com sqladmin.googleapis.com secretmanager.googleapis.com

gcloud artifacts repositories create swe-challenge \
  --repository-format=docker \
  --location=us-central1

gcloud sql instances create swe-postgres \
  --database-version=POSTGRES_16 \
  --region=us-central1 \
  --tier=db-f1-micro

gcloud sql databases create swe_users --instance=swe-postgres
```

Create a database user and store the `DATABASE_URL` in Secret Manager:

```bash
printf "%s" "postgresql+asyncpg://USER:PASSWORD@/swe_users?host=/cloudsql/PROJECT_ID:us-central1:swe-postgres" \
  | gcloud secrets create swe-database-url --data-file=-
```

Update `cloudbuild.yaml` substitutions:

```yaml
_INSTANCE_CONNECTION_NAME: PROJECT_ID:us-central1:swe-postgres
_DATABASE_URL_SECRET: swe-database-url
```

Run Cloud Build:

```bash
gcloud builds submit --config cloudbuild.yaml
```

After deployment, get the public URL:

```bash
gcloud run services describe swe-user-api \
  --region=us-central1 \
  --format="value(status.url)"
```
