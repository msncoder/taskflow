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

### 1. Login

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
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
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

### 2. Get Current User

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
   - `Authorization`: `Bearer YOUR_ACCESS_TOKEN`
4. Click **"Send"**

---

### 3. Get Company Info

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

## 🎯 INVITATION ENDPOINTS

### 4. Send Invitation

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

**409 Conflict** (Email already invited):
```json
{
  "error": "Conflict",
  "detail": "An invitation for this email already exists"
}
```

---

### 5. List Invitations

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

---

### 6. Accept Invitation

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
  "token": "invitation-token-from-email",
  "full_name": "New User Name",
  "password": "securepassword123"
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

**Error Responses:**

**404 Not Found** (Invalid token):
```json
{
  "error": "Not Found",
  "detail": "Invalid invitation token"
}
```

**400 Bad Request** (Already accepted or expired):
```json
{
  "error": "Bad Request",
  "detail": "This invitation has already been accepted"
}
```

---

## 👥 USER MANAGEMENT ENDPOINTS

### 7. List Company Users

**Endpoint:** `GET /users/`

**Permissions:**
- **Admin/Manager**: Can view all users in company
- **Employee**: 403 Forbidden

**Headers:**
```
Authorization: Bearer YOUR_ADMIN_OR_MANAGER_TOKEN
```

**Expected Response (200):**
```json
[
  {
    "id": "user-uuid-1",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "role": "admin",
    "company_id": "company-uuid",
    "is_active": true,
    "created_at": "2026-03-15T..."
  },
  {
    "id": "user-uuid-2",
    "email": "employee@example.com",
    "full_name": "Employee User",
    "role": "employee",
    "company_id": "company-uuid",
    "is_active": true,
    "created_at": "2026-03-16T..."
  }
]
```

---

### 8. Get User Detail

**Endpoint:** `GET /users/{user_id}`

**Permissions:**
- **Admin/Manager**: Can view any user in their company

**Headers:**
```
Authorization: Bearer YOUR_ADMIN_OR_MANAGER_TOKEN
```

**Expected Response (200):**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "full_name": "User Name",
  "role": "employee",
  "company_id": "company-uuid",
  "is_active": true,
  "created_at": "2026-03-15T..."
}
```

**Error Responses:**

**404 Not Found**:
```json
{
  "error": "Not Found",
  "detail": "User not found"
}
```

---

### 9. Update Own Profile

**Endpoint:** `PATCH /users/me`

**Permissions:**
- **All authenticated users**: Can update their own profile

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Request:**
```json
{
  "full_name": "Updated Full Name"
}
```

**Expected Response (200):**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "full_name": "Updated Full Name",
  "role": "employee",
  "company_id": "company-uuid",
  "is_active": true,
  "created_at": "2026-03-15T..."
}
```

---

### 10. Deactivate User

**Endpoint:** `DELETE /users/{user_id}`

**Permissions:**
- **Admin only**: Can deactivate non-admin users

**Headers:**
```
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Expected Response (204):** No content (user deactivated)

**Error Responses:**

**403 Forbidden** (Trying to deactivate self):
```json
{
  "error": "Forbidden",
  "detail": "You cannot deactivate your own account"
}
```

**403 Forbidden** (Trying to deactivate admin):
```json
{
  "error": "Forbidden",
  "detail": "Cannot deactivate admin users"
}
```

**404 Not Found**:
```json
{
  "error": "Not Found",
  "detail": "User not found"
}
```

---

## 📊 Complete Test Flow

```
┌─────────────────────────────────────────────────────────────┐
│  AUTHENTICATION FLOW                                        │
│                                                             │
│  1. POST /auth/login → Save access_token                    │
│  2. GET /auth/me → Verify user info                         │
│  3. GET /company/me → Verify company info                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  INVITATION FLOW                                            │
│                                                             │
│  1. POST /invitations/ → Create invitation                  │
│  2. GET /invitations/ → List all invitations                │
│  3. POST /invitations/accept → Accept & create account      │
│  4. POST /auth/login (as new user) → Verify login works     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  USER MANAGEMENT FLOW                                       │
│                                                             │
│  1. GET /users/ → List all company users                    │
│  2. GET /users/{id} → Get user details                      │
│  3. PATCH /users/me → Update own profile                    │
│  4. DELETE /users/{id} → Deactivate user (Admin only)       │
└─────────────────────────────────────────────────────────────┘
```

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
   invitation_token = (leave empty, will be set after creating invitation)
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

## 🧪 Quick Test with cURL

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"password\":\"password123\"}"
```

### Send Invitation
```bash
curl -X POST "http://localhost:8000/api/v1/invitations/" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_TOKEN" ^
  -d "{\"email\":\"newuser@example.com\",\"role\":\"employee\"}"
```

### List Users
```bash
curl -X GET "http://localhost:8000/api/v1/users/" ^
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update Profile
```bash
curl -X PATCH "http://localhost:8000/api/v1/users/me" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_TOKEN" ^
  -d "{\"full_name\":\"New Name\"}"
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
| Accept invitation | ✅ | ✅ | ✅ |
| List company users | ✅ | ✅ | ❌ |
| Get user detail | ✅ | ✅ | ❌ |
| Update own profile | ✅ | ✅ | ✅ |
| Deactivate users | ✅ | ❌ | ❌ |

---

*Generated: 2026-03-18 | TaskFlow SaaS API v0.6.0*
