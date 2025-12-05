# JWT Authentication Testing Guide

## Overview
Your API now has JWT (JSON Web Token) authentication. This means:
- **Public endpoints**: Anyone can access (GET requests)
- **Protected endpoints**: Require authentication token (POST, PUT, DELETE)

## Setup

### 1. Install New Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Delete Old Database (to create new tables with User model)
```powershell
Remove-Item .\instance\data.db -Force
```

### 3. Start the Application
```powershell
python app.py
```

---

## Testing Authentication Flow

### Step 1: Register a New User

**Endpoint:** `POST /register`

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepassword123"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "username": "testuser"
}
```

---

### Step 2: Login to Get Access Token

**Endpoint:** `POST /login`

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepassword123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": 1,
  "username": "testuser"
}
```

**⚠️ IMPORTANT:** Copy the `access_token` value - you'll need it for protected endpoints!

---

### Step 3: Get Your Profile (Protected Route)

**Endpoint:** `GET /user`

```bash
curl -X GET http://localhost:5000/user \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

Replace `YOUR_ACCESS_TOKEN_HERE` with the token from Step 2.

**Expected Response:**
```json
{
  "id": 1,
  "username": "testuser"
}
```

---

## Testing Protected Endpoints

### Create Specialization (Now Requires Authentication)

**Without Token (Will Fail):**
```bash
curl -X POST http://localhost:5000/specialization \
  -H "Content-Type: application/json" \
  -d '{"name": "Data Science"}'
```

**Expected Error:**
```json
{
  "msg": "Missing Authorization Header"
}
```

**With Token (Will Succeed):**
```bash
curl -X POST http://localhost:5000/specialization \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -d '{"name": "Data Science"}'
```

**Expected Response:**
```json
{
  "id": "abc123...",
  "name": "Data Science",
  "course_items": []
}
```

---

### Update Specialization (Protected)

```bash
curl -X PUT http://localhost:5000/specialization/SPECIALIZATION_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -d '{"name": "Advanced Data Science"}'
```

---

### Delete Specialization (Protected)

```bash
curl -X DELETE http://localhost:5000/specialization/SPECIALIZATION_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## Testing with PowerShell

### Register User
```powershell
$registerBody = @{
    username = "testuser"
    password = "securepassword123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/register" `
    -Method POST `
    -ContentType "application/json" `
    -Body $registerBody
```

### Login and Save Token
```powershell
$loginBody = @{
    username = "testuser"
    password = "securepassword123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5000/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $loginBody

$token = $response.access_token
Write-Host "Token: $token"
```

### Use Token for Protected Request
```powershell
$headers = @{
    Authorization = "Bearer $token"
    "Content-Type" = "application/json"
}

$specBody = @{
    name = "Data Science"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/specialization" `
    -Method POST `
    -Headers $headers `
    -Body $specBody
```

---

## Testing with Swagger UI

1. Open browser: `http://localhost:5000/swagger`

2. **Register a user:**
   - Expand `POST /register`
   - Click "Try it out"
   - Enter username and password
   - Click "Execute"

3. **Login:**
   - Expand `POST /login`
   - Click "Try it out"
   - Enter same username and password
   - Click "Execute"
   - **Copy the access_token from response**

4. **Authorize Swagger:**
   - Click the green "Authorize" button at top
   - Enter: `Bearer YOUR_ACCESS_TOKEN_HERE`
   - Click "Authorize"
   - Click "Close"

5. **Test protected endpoints:**
   - Now all requests will include your token automatically
   - Try creating a specialization with POST /specialization

---

## Testing with Postman

### 1. Register User
- Method: `POST`
- URL: `http://localhost:5000/register`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "username": "testuser",
  "password": "securepassword123"
}
```

### 2. Login
- Method: `POST`
- URL: `http://localhost:5000/login`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "username": "testuser",
  "password": "securepassword123"
}
```
- **Copy the access_token from response**

### 3. Set Authorization for Protected Requests
- Go to "Authorization" tab
- Type: "Bearer Token"
- Token: Paste your access_token

### 4. Test Protected Endpoint
- Method: `POST`
- URL: `http://localhost:5000/specialization`
- Authorization: Bearer Token (already set)
- Body (raw JSON):
```json
{
  "name": "Data Science"
}
```

---

## Current API Endpoints

### Public Endpoints (No Authentication Required)
- `GET /specialization` - List all specializations
- `GET /specialization/<id>` - Get specific specialization
- `GET /course_item` - List all course items
- `GET /course_item/<id>` - Get specific course item

### Protected Endpoints (Require JWT Token)
- `POST /register` - Register new user
- `POST /login` - Login and get token
- `GET /user` - Get current user profile
- `POST /specialization` - Create specialization
- `PUT /specialization/<id>` - Update specialization
- `DELETE /specialization/<id>` - Delete specialization

**Note:** Course item endpoints are NOT protected yet. You can add `@jwt_required()` to them following the same pattern.

---

## Common Issues & Solutions

### Issue: "Missing Authorization Header"
**Solution:** Add the Authorization header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

### Issue: "Token has expired"
**Solution:** Login again to get a new token (default expiry: 1 hour)

### Issue: "Invalid username or password"
**Solution:** Check username/password are correct, or register a new user

### Issue: "Username already exists"
**Solution:** Use a different username or login with existing credentials

---

## Security Best Practices

### For Production:
1. **Change JWT Secret Key:**
   - Set environment variable: `JWT_SECRET_KEY=your-very-long-random-string`
   - Never commit secret key to git

2. **Use HTTPS:**
   - JWT tokens should only be sent over HTTPS in production

3. **Add Token Expiration:**
   - Configure in app.py:
   ```python
   app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
   ```

4. **Add Refresh Tokens:**
   - Implement refresh token endpoint for long-lived sessions

5. **Add User Roles:**
   - Extend UserModel with role field (admin, user, etc.)
   - Use custom decorators to check roles

---

## Example Complete Test Script (PowerShell)

```powershell
# Test script for JWT authentication

# 1. Register
Write-Host "1. Registering user..." -ForegroundColor Cyan
$registerBody = @{
    username = "testuser"
    password = "test123"
} | ConvertTo-Json

$registerResponse = Invoke-RestMethod -Uri "http://localhost:5000/register" `
    -Method POST `
    -ContentType "application/json" `
    -Body $registerBody
Write-Host "Registered: $($registerResponse.username)" -ForegroundColor Green

# 2. Login
Write-Host "`n2. Logging in..." -ForegroundColor Cyan
$loginBody = @{
    username = "testuser"
    password = "test123"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "http://localhost:5000/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $loginBody

$token = $loginResponse.access_token
Write-Host "Token received!" -ForegroundColor Green

# 3. Get Profile
Write-Host "`n3. Getting user profile..." -ForegroundColor Cyan
$headers = @{
    Authorization = "Bearer $token"
}

$profile = Invoke-RestMethod -Uri "http://localhost:5000/user" `
    -Method GET `
    -Headers $headers
Write-Host "Profile: $($profile.username)" -ForegroundColor Green

# 4. Create Specialization
Write-Host "`n4. Creating specialization..." -ForegroundColor Cyan
$headers["Content-Type"] = "application/json"
$specBody = @{
    name = "Data Science"
} | ConvertTo-Json

$spec = Invoke-RestMethod -Uri "http://localhost:5000/specialization" `
    -Method POST `
    -Headers $headers `
    -Body $specBody
Write-Host "Created: $($spec.name) (ID: $($spec.id))" -ForegroundColor Green

Write-Host "`nAll tests passed!" -ForegroundColor Green
```

Save this as `test-jwt.ps1` and run with:
```powershell
.\test-jwt.ps1
```

---

## Next Steps

1. **Protect course_item endpoints** - Add `@jwt_required()` to POST, PUT, DELETE in `resources/course_item.py`
2. **Add user roles** - Implement admin vs regular user permissions
3. **Add refresh tokens** - Allow users to refresh expired tokens
4. **Add password reset** - Email-based password recovery
5. **Add rate limiting** - Prevent brute force login attempts
