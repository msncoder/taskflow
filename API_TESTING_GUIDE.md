# API Testing Guide with Requestly

## 📋 Test Credentials

```
Email: test@example.com
Password: password123
```

---

## 🔧 Requestly Setup

### 1. Install Requestly

1. Go to [Requestly Desktop](https://requestly.com/)
2. Download and install for Windows
3. Open Requestly Desktop

### 2. Create API Collection

1. Click **"API Client"** in the left sidebar
2. Click **"New Collection"**
3. Name it: `TaskFlow SaaS`
4. Base URL: `http://localhost:8000/api/v1`

---

## 📝 Test Endpoints

### 1. Register New Admin (Optional - Skip if test user exists)

**Endpoint:** `POST /auth/register`

**Request:**
```json
{
  "email": "newadmin@example.com",
  "full_name": "New Admin User",
  "password": "password123",
  "company_name": "New Company Inc"
}
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Requestly Setup:**
1. Click **"New Request"** → **"POST"**
2. URL: `{{base_url}}/auth/register`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON): Paste the JSON above
5. Click **"Send"**

---

### 2. Login

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI...",
  "token_type": "bearer"
}
```

**Requestly Setup:**
1. Click **"New Request"** → **"POST"**
2. URL: `{{base_url}}/auth/login`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON): Paste the JSON above
5. Click **"Send"**
6. **Save the `access_token`** from response for next requests

---

### 3. Get Current User Info (Protected)

**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Expected Response (200):**
```json
{
  "id": "uuid-here",
  "email": "test@example.com",
  "full_name": "Test Admin",
  "role": "admin",
  "company_id": "uuid-here",
  "is_active": true,
  "created_at": "2026-03-15T..."
}
```

**Requestly Setup:**
1. Click **"New Request"** → **"GET"**
2. URL: `{{base_url}}/auth/me`
3. Headers tab:
   - `Authorization`: `Bearer eyJhbGciOiJIUzI1NiIs...` (paste your token)
4. Click **"Send"**

---

### 4. Get Company Info (Admin Only)

**Endpoint:** `GET /company/me`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Expected Response (200):**
```json
{
  "id": "uuid-here",
  "name": "Test Company",
  "slug": "test-company",
  "created_at": "2026-03-15T..."
}
```

**Requestly Setup:**
1. Click **"New Request"** → **"GET"**
2. URL: `{{base_url}}/company/me`
3. Headers tab:
   - `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
4. Click **"Send"**

---

### 5. Refresh Token

**Endpoint:** `POST /auth/refresh`

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Requestly Setup:**
1. Click **"New Request"** → **"POST"**
2. URL: `{{base_url}}/auth/refresh`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON): Paste refresh token from login response
5. Click **"Send"**

---

### 6. Test Without Authentication (Should Fail)

**Endpoint:** `GET /auth/me`

**Expected Response (401):**
```json
{
  "error": "Unauthorized",
  "detail": "Missing authentication token"
}
```

**Requestly Setup:**
1. Click **"New Request"** → **"GET"**
2. URL: `{{base_url}}/auth/me`
3. **Do NOT add Authorization header**
4. Click **"Send"**
5. Verify you get 401 Unauthorized

---

## 🔐 Using Environment Variables in Requestly

### Create Environment

1. Click **"Environments"** in left sidebar
2. Click **"New Environment"**
3. Name: `Local Development`
4. Add variables:
   ```
   base_url = http://localhost:8000/api/v1
   access_token = (leave empty, will be set after login)
   refresh_token = (leave empty, will be set after login)
   ```

### Auto-Save Tokens with Tests

In your Login request, add this **Test Script**:

```javascript
// Parse response
const response = pm.response.json();

// Save tokens to environment
pm.environment.set('access_token', response.access_token);
pm.environment.set('refresh_token', response.refresh_token);

console.log('Tokens saved!');
```

Then in protected requests, use:
```
Authorization: Bearer {{access_token}}
```

---

## 📊 Complete Test Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. POST /auth/login                                        │
│     → Save access_token and refresh_token                   │
│                                                             │
│  2. GET /auth/me (with access_token)                        │
│     → Verify user info                                      │
│                                                             │
│  3. GET /company/me (with access_token)                     │
│     → Verify company info                                   │
│                                                             │
│  4. POST /auth/refresh (with refresh_token)                 │
│     → Get new tokens                                        │
│                                                             │
│  5. GET /auth/me (without token)                            │
│     → Verify 401 Unauthorized                               │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚠️ Troubleshooting

### 401 Unauthorized
- Check if `Authorization` header is present
- Verify token format: `Bearer <token>` (note the space)
- Token might be expired (use refresh endpoint)

### 500 Internal Server Error
- Check server logs: `cd backend && poetry run uvicorn app.main:app --reload`
- Verify database connection in `.env`
- Check if tables exist: `poetry run alembic check`

### Connection Refused
- Ensure server is running: `http://localhost:8000/health`
- Check if port 8000 is available

---

## 🧪 Quick Test with cURL

If Requestly is not available, use cURL:

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"password\":\"password123\"}"

# Get user info (replace TOKEN)
curl -X GET "http://localhost:8000/api/v1/auth/me" ^
  -H "Authorization: Bearer TOKEN"

# Get company info
curl -X GET "http://localhost:8000/api/v1/company/me" ^
  -H "Authorization: Bearer TOKEN"
```

---

*Generated: 2026-03-15 | TaskFlow SaaS API v0.5.0*
