# API Testing Guide with Requestly

## 📋 Test Credentials

```
Admin Email: test@example.com
Admin Password: password123
```

**Note:** Run `python seed_test_data.py` to create the test user if it doesn't exist.

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

### 1. Login (Admin)

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

### 2. Get Current User Info (Protected)

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

### 3. Get Company Info (Admin Only)

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

## 🎯 Invitation Endpoints

### 4. Send Invitation (Admin/Manager)

**Endpoint:** `POST /invitations/`

**Permissions:**
- **Admin**: Can invite managers and employees
- **Manager**: Can only invite employees
- **Employee**: Cannot send invitations (403 Forbidden)

**Headers:**
```
Authorization: Bearer YOUR_ADMIN_OR_MANAGER_TOKEN
Content-Type: application/json
```

**Request (Invite Manager):**
```json
{
  "email": "newmanager@example.com",
  "role": "manager"
}
```

**Request (Invite Employee):**
```json
{
  "email": "newemployee@example.com",
  "role": "employee"
}
```

**Expected Response (201):**
```json
{
  "id": "invitation-uuid-here",
  "email": "newmanager@example.com",
  "role": "manager",
  "is_accepted": false,
  "expires_at": "2026-03-18T12:00:00Z"
}
```

**Error Responses:**

**403 Forbidden** (Manager trying to invite manager):
```json
{
  "error": "Forbidden",
  "detail": "Managers can only invite employees"
}
```

**403 Forbidden** (Employee trying to invite):
```json
{
  "error": "Forbidden",
  "detail": "Employees cannot send invitations"
}
```

**409 Conflict** (Email already invited):
```json
{
  "error": "Conflict",
  "detail": "An invitation for this email already exists"
}
```

**Requestly Setup:**
1. Click **"New Request"** → **"POST"**
2. URL: `{{base_url}}/invitations/`
3. Headers tab:
   - `Authorization`: `Bearer YOUR_ADMIN_TOKEN`
   - `Content-Type`: `application/json`
4. Body (raw JSON): Paste invitation request
5. Click **"Send"**
6. **Save the invitation token** for acceptance testing

---

### 5. List All Invitations (Admin Only)

**Endpoint:** `GET /invitations/`

**Permissions:**
- **Admin**: Can view all company invitations
- **Manager/Employee**: 403 Forbidden

**Headers:**
```
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Expected Response (200):**
```json
[
  {
    "id": "invitation-uuid-1",
    "email": "manager1@example.com",
    "role": "manager",
    "is_accepted": false,
    "expires_at": "2026-03-18T12:00:00Z"
  },
  {
    "id": "invitation-uuid-2",
    "email": "employee1@example.com",
    "role": "employee",
    "is_accepted": true,
    "expires_at": "2026-03-18T12:00:00Z"
  }
]
```

**Requestly Setup:**
1. Click **"New Request"** → **"GET"**
2. URL: `{{base_url}}/invitations/`
3. Headers tab:
   - `Authorization`: `Bearer YOUR_ADMIN_TOKEN`
4. Click **"Send"**

---

### 6. Accept Invitation (Public - No Auth Required)

**Endpoint:** `POST /invitations/accept`

**Permissions:**
- **Public**: No authentication required (token in request body)

**Headers:**
```
Content-Type: application/json
```

**Request:**
```json
{
  "token": "invitation-token-from-email-or-invitation-response",
  "full_name": "New User Name",
  "password": "securepassword123"
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

**Error Responses:**

**404 Not Found** (Invalid token):
```json
{
  "error": "Not Found",
  "detail": "Invalid invitation token"
}
```

**400 Bad Request** (Already accepted):
```json
{
  "error": "Bad Request",
  "detail": "This invitation has already been accepted"
}
```

**400 Bad Request** (Expired):
```json
{
  "error": "Bad Request",
  "detail": "This invitation has expired"
}
```

**409 Conflict** (Email already registered):
```json
{
  "error": "Conflict",
  "detail": "Email already registered"
}
```

**Requestly Setup:**
1. Click **"New Request"** → **"POST"**
2. URL: `{{base_url}}/invitations/accept`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON): Paste acceptance request with token
5. Click **"Send"**
6. **Save the tokens** to login as the new user

---

## 🔐 Using Environment Variables in Requestly

### Create Environment

1. Click **"Environments"** in left sidebar
2. Click **"New Environment"**
3. Name: `Local Development`
4. Add variables:
   ```
   base_url = http://localhost:8000/api/v1
   admin_token = (leave empty, will be set after admin login)
   manager_token = (leave empty, will be set after manager login)
   invitation_token = (leave empty, will be set after creating invitation)
   ```

### Auto-Save Tokens with Tests

In your Login request, add this **Test Script**:

```javascript
// Parse response
const response = pm.response.json();

// Save tokens to environment
pm.environment.set('admin_token', response.access_token);
pm.environment.set('refresh_token', response.refresh_token);

console.log('Tokens saved!');
```

Then in protected requests, use:
```
Authorization: Bearer {{admin_token}}
```

---

## 📊 Complete Invitation Test Flow

```
┌─────────────────────────────────────────────────────────────┐
│  INVITATION WORKFLOW                                        │
│                                                             │
│  1. POST /auth/login (as admin)                             │
│     → Save admin access_token                               │
│                                                             │
│  2. POST /invitations/                                      │
│     Body: {"email": "newuser@example.com", "role": "manager"}│
│     Headers: Authorization: Bearer {{admin_token}}          │
│     → Save invitation token from response                   │
│                                                             │
│  3. GET /invitations/                                       │
│     Headers: Authorization: Bearer {{admin_token}}          │
│     → Verify invitation appears in list                     │
│                                                             │
│  4. POST /invitations/accept (no auth)                      │
│     Body: {"token": "TOKEN", "full_name": "New User",       │
│            "password": "password123"}                       │
│     → Save new user tokens                                  │
│                                                             │
│  5. POST /auth/login (as new user)                          │
│     → Verify new user can login                             │
│                                                             │
│  6. GET /auth/me (as new user)                              │
│     Headers: Authorization: Bearer {{new_user_token}}       │
│     → Verify user has correct role (manager/employee)       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 Quick Test with cURL

### Send Invitation (Admin)
```bash
# First login to get token
curl -X POST "http://localhost:8000/api/v1/auth/login" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"password\":\"password123\"}"

# Send invitation (replace TOKEN with access_token from login)
curl -X POST "http://localhost:8000/api/v1/invitations/" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer TOKEN" ^
  -d "{\"email\":\"newuser@example.com\",\"role\":\"manager\"}"
```

### List Invitations (Admin)
```bash
curl -X GET "http://localhost:8000/api/v1/invitations/" ^
  -H "Authorization: Bearer TOKEN"
```

### Accept Invitation (Public)
```bash
curl -X POST "http://localhost:8000/api/v1/invitations/accept" ^
  -H "Content-Type: application/json" ^
  -d "{\"token\":\"INVITATION_TOKEN\",\"full_name\":\"New User\",\"password\":\"password123\"}"
```

---

## ⚠️ Troubleshooting

### 401 Unauthorized
- Check if `Authorization` header is present
- Verify token format: `Bearer <token>` (note the space)
- Token might be expired (use refresh endpoint)

### 403 Forbidden
- User role doesn't have permission for this action
- Admin can do everything, Manager can only invite employees

### 409 Conflict
- Email already invited or already registered in company

### 400 Bad Request (Invitation)
- Invitation already accepted or expired (48 hours)

### 500 Internal Server Error
- Check server logs: `cd backend && uvicorn app.main:app --reload`
- Verify database connection in `.env`
- Check if tables exist: `alembic check`

### Connection Refused
- Ensure server is running: `http://localhost:8000/health`
- Check if port 8000 is available

---

## 📋 Role Permissions Matrix

| Action | Admin | Manager | Employee |
|--------|-------|---------|----------|
| Send invitation (manager) | ✅ | ❌ | ❌ |
| Send invitation (employee) | ✅ | ✅ | ❌ |
| List all invitations | ✅ | ❌ | ❌ |
| Accept invitation | N/A | N/A | N/A |

---

*Generated: 2026-03-16 | TaskFlow SaaS API v0.6.0*
