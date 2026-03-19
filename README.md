# TaskFlow SaaS — Backend

FastAPI-based backend for TaskFlow SaaS platform — a multi-tenant task management system with role-based access control.

## 🚀 Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (Neon DB)
- **ORM:** SQLAlchemy 2.x (Async)
- **Migrations:** Alembic
- **Auth:** JWT (python-jose)
- **Password Hashing:** bcrypt
- **Package Manager:** Poetry
- **Python:** 3.10+

---

## ✅ Completed Phases

### Phase 0 — Bootstrap & Infrastructure ✅

- [x] Project initialization with FastAPI
- [x] Database setup with async SQLAlchemy
- [x] Alembic migrations configured
- [x] Core security (JWT, password hashing)
- [x] Custom exception handlers
- [x] Role-based access control

### Phase 1 — Feature: Company ✅

- [x] Company model with auto-generated slug
- [x] Company service layer
- [x] Company router (`GET /company/me`)

### Phase 2 — Feature: Auth ✅

- [x] User model with roles (admin, manager, employee)
- [x] Login endpoint (`POST /auth/login`)
- [x] Token refresh (`POST /auth/refresh`)
- [x] Current user endpoint (`GET /auth/me`)
- [x] Password hashing with bcrypt

### Phase 3 — Feature: Invitation ✅

- [x] Invitation model with 48-hour expiry
- [x] Send invitation (`POST /invitations/`)
- [x] List invitations (`GET /invitations/`)
- [x] Accept invitation (`POST /invitations/accept`)
- [x] Role-based invitation permissions

### Phase 4 — Feature: User Management ✅

- [x] List company users (`GET /users/`)
- [x] Get user detail (`GET /users/{user_id}`)
- [x] Update own profile (`PATCH /users/me`)
- [x] Deactivate user (`DELETE /users/{user_id}`)

### Phase 5 — Feature: Task Management ✅

- [x] Task model with relationships
- [x] Task CRUD operations
- [x] Role-based task assignment
- [x] Task status toggling
- [x] Company isolation

### Phase 6 — Feature: Comments ✅

- [x] Comment model with cascade delete
- [x] Comment schemas with nested author
- [x] Comment service with task access validation
- [x] Comment router (add, list, delete)
- [x] Task access control for comments

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── __init__.py            # Core exports
│   │   ├── config.py              # Settings (pydantic-settings)
│   │   ├── security.py            # JWT & password hashing
│   │   ├── dependencies.py        # get_db, get_current_user, require_role
│   │   └── exceptions.py          # Custom HTTP exceptions
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py                # SQLAlchemy Base
│   │   └── session.py             # Async engine & session
│   ├── features/
│   │   ├── auth/                  # Authentication
│   │   ├── company/               # Company/Tenant management
│   │   ├── invitation/            # User invitations
│   │   ├── user/                  # User management
│   │   └── task/                  # Task management
│   ├── __init__.py
│   └── main.py                    # FastAPI entry point
├── alembic/
│   ├── env.py                     # Async migrations
│   └── versions/                  # Migration scripts
├── .env.example                   # Environment template
├── requirements.txt               # Python dependencies
├── docker-compose.yml             # Local PostgreSQL
└── seed_test_data.py              # Test data seeder
```

---

## 🛠️ Setup & Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example and edit
copy .env.example .env
```

Update `.env` with your database connection:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host.neon.tech/dbname
SECRET_KEY=<generate-secure-key>
```

### 3. Run Database Migrations

```bash
# Apply all migrations
alembic upgrade head

# Check status
alembic check
```

### 4. Seed Test Data

```bash
# Create test user (test@example.com / password123)
python seed_test_data.py
```

### 5. Start Development Server

```bash
uvicorn app.main:app --reload
```

Visit: **http://localhost:8000/health**

---

## 📝 Available Commands

| Command | Description |
|---------|-------------|
| `uvicorn app.main:app --reload` | Start dev server |
| `alembic revision --autogenerate -m "msg"` | Create migration |
| `alembic upgrade head` | Apply migrations |
| `alembic downgrade -1` | Rollback last migration |
| `alembic check` | Check migration status |
| `python seed_test_data.py` | Create test user |

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
| `SMTP_HOST` | SMTP server (for invitations) | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | SMTP username | - |
| `SMTP_PASSWORD` | SMTP password | - |

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

### Invitation

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `email` | String(255) | Invitee email |
| `role` | Enum | `manager`, `employee` |
| `company_id` | UUID | FK to companies |
| `token` | String(255) | Unique invitation token |
| `is_accepted` | Boolean | Acceptance status |
| `expires_at` | DateTime | 48-hour expiry |
| `created_at` | DateTime | Creation timestamp |

### Task

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `title` | String(255) | Task title |
| `description` | Text | Task description |
| `is_completed` | Boolean | Completion status (default: False) |
| `company_id` | UUID | FK to companies |
| `created_by_id` | UUID | FK to task creator |
| `assigned_to_id` | UUID | FK to assigned user (nullable) |
| `due_date` | Date | Task due date (nullable) |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

---

## 🔒 User Roles

| Role | Permissions |
|------|-------------|
| `admin` | Full access to all features, can deactivate users, delete tasks |
| `manager` | Can invite employees, view users, create/assign tasks to employees |
| `employee` | Can view assigned tasks, toggle completion, update own profile |

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/login` | - | Login with email/password |
| POST | `/api/v1/auth/refresh` | - | Refresh access token |
| GET | `/api/v1/auth/me` | Required | Get current user |

### Company

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/company/me` | Admin | Get current user's company |

### Invitations

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/invitations/` | Admin/Manager | Send invitation |
| GET | `/api/v1/invitations/` | Admin | List all invitations |
| POST | `/api/v1/invitations/accept` | - | Accept invitation |

### Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/users/` | Admin/Manager | List company users |
| GET | `/api/v1/users/{id}` | Admin/Manager | Get user detail |
| PATCH | `/api/v1/users/me` | All | Update own profile |
| DELETE | `/api/v1/users/{id}` | Admin | Deactivate user |

### Tasks

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/tasks/` | Admin/Manager | Create task |
| GET | `/api/v1/tasks/` | All | List tasks (role-filtered) |
| GET | `/api/v1/tasks/{id}` | All | Get task detail |
| PATCH | `/api/v1/tasks/{id}` | Creator/Admin | Update task |
| PATCH | `/api/v1/tasks/{id}/toggle-complete` | Assigned | Toggle completion |
| DELETE | `/api/v1/tasks/{id}` | Admin | Delete task |

### Comments

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/tasks/{id}/comments/` | Task access | Add comment |
| GET | `/api/v1/tasks/{id}/comments/` | Task access | List comments |
| DELETE | `/api/v1/tasks/{id}/comments/{id}` | Author/Admin | Delete comment |

---

## 🧪 Testing

### Test Credentials

After running `python seed_test_data.py`:

```
Email: test@example.com
Password: password123
Role: admin
```

### Run API Tests

See `API_TESTING_GUIDE.md` for detailed endpoint testing instructions.

### Test Results

**All Phases (0-6): 56/56 tests passed (100% success rate)**

| Phase | Feature | Endpoints | Tests |
|-------|---------|-----------|-------|
| Phase 1 | Company | 1 | 3 ✅ |
| Phase 2 | Auth | 3 | 7 ✅ |
| Phase 3 | Invitation | 3 | 7 ✅ |
| Phase 4 | Users | 4 | 11 ✅ |
| Phase 5 | Tasks | 6 | 11 ✅ |
| Phase 6 | Comments | 3 | 17 ✅ |
| **Total** | | **20** | **56 ✅** |

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
- `bcrypt` — Password hashing
- `python-multipart` — Form data

---

## 🔜 Upcoming Phases

### Phase 6 — Feature: Comments
- Comment model
- Comment schemas, service, router
- Task comment threads

### Phase 7 — Testing
- Unit tests
- Integration tests
- API test suite

### Phase 8 — Frontend (Next.js)
- React dashboard
- Authentication UI
- Task management interface

---

## 📄 License

MIT

---

*Generated: 2026-03-18 | TaskFlow SaaS Backend v0.8.0*
