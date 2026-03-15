# TaskFlow SaaS — Backend

FastAPI-based backend for TaskFlow SaaS platform.

## 🚀 Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (Neon DB)
- **ORM:** SQLAlchemy 2.x (Async)
- **Migrations:** Alembic
- **Auth:** JWT (python-jose)
- **Password Hashing:** passlib + bcrypt
- **Package Manager:** Poetry
- **Python:** 3.11+

---

## ✅ Completed Tasks

### Task 0.1 — Initialize Project

- [x] Created `backend/` directory with `app/` structure
- [x] Created `requirements.txt` with all dependencies
- [x] Created `.env` and `.env.example` files
- [x] Created `app/core/config.py` using `pydantic-settings`
- [x] Created `app/main.py` — FastAPI app with health check endpoint
- [x] Initialized Poetry project with all dependencies

### Task 0.2 — Database Setup

- [x] Created `docker-compose.yml` with PostgreSQL 15 service
- [x] Created `app/db/base.py` — SQLAlchemy `DeclarativeBase`
- [x] Created `app/db/session.py` — async engine + `AsyncSession`
- [x] Initialized Alembic (`alembic init alembic`)
- [x] Configured `alembic/env.py` for async engine and Neon DB

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # Settings via pydantic-settings
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py            # SQLAlchemy Base
│   │   └── session.py         # Async engine & session factory
│   ├── features/
│   │   └── __init__.py        # Feature modules (coming soon)
│   ├── __init__.py
│   └── main.py                # FastAPI entry point
├── alembic/
│   ├── env.py                 # Alembic async config
│   └── versions/              # Migration scripts
├── tests/                     # Test suite (coming soon)
├── .env                       # Environment variables (DO NOT COMMIT)
├── .env.example               # Example environment template
├── .gitignore                 # Git ignore rules
├── alembic.ini                # Alembic configuration
├── docker-compose.yml         # Local PostgreSQL
├── pyproject.toml             # Poetry dependencies
├── poetry.lock                # Locked dependencies
└── requirements.txt           # Pip requirements (alternative)
```

---

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.11+
- Poetry (`curl -sSL https://install.python-poetry.org | python3 -`)
- Docker (optional, for local PostgreSQL)

### 1. Install Dependencies

```bash
cd backend
poetry install
```

### 2. Configure Environment

```bash
# Copy example and edit
cp .env.example .env
```

Update `.env` with your Neon DB connection string:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host.neon.tech/dbname
SECRET_KEY=<generate-with: poetry run python -c "import secrets; print(secrets.token_urlsafe(48))">
```

### 3. Run Database Migrations

```bash
# Check migration status
poetry run alembic check

# Create initial migration
poetry run alembic revision --autogenerate -m "initial"

# Apply migrations
poetry run alembic upgrade head
```

### 4. Start Development Server

```bash
poetry run uvicorn app.main:app --reload
```

Visit: **http://localhost:8000/health**

---

## 📝 Available Commands

| Command | Description |
|---------|-------------|
| `poetry run uvicorn app.main:app --reload` | Start dev server |
| `poetry run alembic revision --autogenerate -m "msg"` | Create migration |
| `poetry run alembic upgrade head` | Apply migrations |
| `poetry run alembic downgrade -1` | Rollback last migration |
| `poetry run alembic check` | Check migration status |
| `poetry run pytest` | Run tests |
| `docker-compose up -d` | Start local PostgreSQL |

---

## 🔐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string (required) | - |
| `SECRET_KEY` | JWT signing key (required) | - |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | `7` |
| `CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:3000"]` |
| `SMTP_HOST` | SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | SMTP username | - |
| `SMTP_PASSWORD` | SMTP password | - |
| `SMTP_FROM_EMAIL` | From email | `noreply@taskflow.com` |

---

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest tests/test_auth.py
```

---

## 📦 Dependencies

**Core:**
- `fastapi` — Web framework
- `uvicorn` — ASGI server
- `sqlalchemy[asyncio]` — Async ORM
- `asyncpg` — PostgreSQL async driver
- `alembic` — Database migrations
- `pydantic-settings` — Settings management
- `python-jose[cryptography]` — JWT handling
- `passlib[bcrypt]` — Password hashing
- `python-multipart` — Form data

**Development:**
- `pytest` — Testing framework
- `pytest-asyncio` — Async test support
- `httpx` — Async HTTP client

---

## 🐳 Docker (Local Development)

```bash
# Start PostgreSQL
docker-compose up -d

# View logs
docker-compose logs -f postgres

# Stop
docker-compose down
```

**Local DB URL:**
```
postgresql+asyncpg://taskflow:taskflow_password@localhost:5432/taskflow
```

---

## 🔜 Next Steps

### Phase 1 — Feature: Company
- Company model, schemas, service, router

### Phase 2 — Feature: Auth
- User model, registration, login, JWT tokens

### Phase 3 — Feature: Invitation
- Invitation model, send/accept invite flow

### Phase 4 — Feature: User Management
- User CRUD, role management

### Phase 5 — Feature: Task Management
- Task CRUD, role-based access

### Phase 6 — Feature: Comments
- Comment system for tasks

---

## 📄 License

MIT

---

*Generated: 2026-03-15 | TaskFlow SaaS Backend v0.1.0*
