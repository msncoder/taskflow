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

### Task 0.3 — Core Security & Dependencies

- [x] Created `app/core/security.py`:
  - `hash_password(plain: str) → str`
  - `verify_password(plain: str, hashed: str) → bool`
  - `create_access_token(data: dict) → str`
  - `create_refresh_token(data: dict) → str`
  - `decode_token(token: str) → dict`
- [x] Created `app/core/dependencies.py`:
  - `get_db()` → yields `AsyncSession`
  - `get_current_user()` → decodes JWT, returns `User`
  - `require_role(*roles)` → role-based guard
- [x] Created `app/core/exceptions.py` — custom 401, 403, 404 handlers
- [x] Created `app/features/company/models.py` — Company model
- [x] Created `app/features/user/models.py` — User model with roles
- [x] Generated and applied initial Alembic migration

**✔ Deliverable:** `GET /health` returns `{"status": "ok"}`. DB connects. Alembic can run migrations.

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── __init__.py            # Exports all core modules
│   │   ├── config.py              # Settings via pydantic-settings
│   │   ├── security.py            # Password hashing & JWT tokens
│   │   ├── dependencies.py        # get_db, get_current_user, require_role
│   │   └── exceptions.py          # Custom HTTP exceptions
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py                # SQLAlchemy Base (AsyncAttrs)
│   │   └── session.py             # Async engine & session factory
│   ├── features/
│   │   ├── __init__.py
│   │   ├── company/
│   │   │   ├── __init__.py
│   │   │   └── models.py          # Company model
│   │   ├── user/
│   │   │   ├── __init__.py
│   │   │   └── models.py          # User model with roles
│   │   └── auth/
│   │       └── __init__.py
│   ├── __init__.py
│   └── main.py                    # FastAPI entry point + exception handlers
├── alembic/
│   ├── env.py                     # Alembic async config
│   ├── versions/                  # Migration scripts
│   └── README
├── tests/                         # Test suite (coming soon)
├── .env                           # Environment variables (DO NOT COMMIT)
├── .env.example                   # Example environment template
├── .gitignore                     # Git ignore rules
├── alembic.ini                    # Alembic configuration
├── docker-compose.yml             # Local PostgreSQL
├── pyproject.toml                 # Poetry dependencies
├── poetry.lock                    # Locked dependencies
└── requirements.txt               # Pip requirements (alternative)
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

# Create new migration (when models change)
poetry run alembic revision --autogenerate -m "description"

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
- `httpx` — Async HTTP client
- `psycopg2-binary` — PostgreSQL sync driver (for Alembic)

**Development:**
- `pytest` — Testing framework
- `pytest-asyncio` — Async test support

---

## 🗄️ Database Models

### Company

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `name` | String(255) | Company name |
| `slug` | String(100) | Unique slug (auto-generated) |
| `created_at` | DateTime | Creation timestamp |

### User

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `email` | String(255) | Unique email |
| `full_name` | String(255) | User's full name |
| `hashed_password` | String(255) | Bcrypt hashed password |
| `role` | Enum | `admin`, `manager`, `employee` |
| `company_id` | UUID | FK to companies |
| `is_active` | Boolean | Account status |
| `created_at` | DateTime | Creation timestamp |

**User Roles:**
- `admin` — Full access to company
- `manager` — Can invite employees, create tasks
- `employee` — Can view assigned tasks, toggle complete

---

## 🔒 Security Features

### Password Hashing
```python
from app.core.security import hash_password, verify_password

hashed = hash_password("my_secure_password")
is_valid = verify_password("my_secure_password", hashed)
```

### JWT Tokens
```python
from app.core.security import create_access_token, create_refresh_token, verify_token

access = create_access_token({"sub": user_id})
refresh = create_refresh_token({"sub": user_id})
payload = verify_token(access, token_type="access")
```

### Protected Endpoints
```python
from fastapi import Depends
from app.core.dependencies import get_current_user, require_role, CurrentUser, AdminUser

@app.get("/protected")
async def protected(current_user: CurrentUser):
    return {"user": current_user.email}

@app.get("/admin-only")
async def admin_only(admin: AdminUser):
    return {"message": "Admin access granted"}

@app.get("/manager-or-admin")
async def manager_or_admin(user: CurrentUser = Depends(require_role("manager", "admin"))):
    return {"message": "Manager or admin access"}
```

### Custom Exceptions
```python
from app.core.exceptions import NotFoundException, ForbiddenException

@app.get("/items/{item_id}")
async def get_item(item_id: str):
    item = await get_item_from_db(item_id)
    if not item:
        raise NotFoundException("Item not found")
    return item
```

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
- [ ] Company schemas (Create, Read)
- [ ] Company service layer
- [ ] Company router (CRUD endpoints)

### Phase 2 — Feature: Auth
- [ ] Auth schemas (Register, Login, Token)
- [ ] Auth service (register, login, refresh tokens)
- [ ] Auth router (`/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/me`)

### Phase 3 — Feature: Invitation
- [ ] Invitation model
- [ ] Invitation schemas, service, router
- [ ] Email sending with SMTP

### Phase 4 — Feature: User Management
- [ ] User schemas, service, router
- [ ] User CRUD operations
- [ ] Role management

### Phase 5 — Feature: Task Management
- [ ] Task model
- [ ] Task schemas, service, router
- [ ] Role-based task access

### Phase 6 — Feature: Comments
- [ ] Comment model
- [ ] Comment schemas, service, router

---

## 📄 License

MIT

---

*Generated: 2026-03-15 | TaskFlow SaaS Backend v0.1.0*
