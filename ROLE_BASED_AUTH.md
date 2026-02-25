# Role-Based Authentication System

## Overview

This implementation provides a complete role-based authentication system with three user roles:

- **buyer**: Regular users who can browse and bid on auctions
- **seller**: Users who can create and manage auctions (requires admin approval)
- **admin**: System administrators with full control

## Features

✅ **Public Registration** (buyer or seller only)
✅ **Seller Approval Workflow** (sellers are pending until admin approval)
✅ **JWT Tokens with Role Claims**
✅ **Role-Based Route Protection** (@role_required, @admin_required, @seller_required)
✅ **Admin CLI Commands** (create first admin, manage users, approve sellers)
✅ **Login Blocking for Unapproved Sellers**

---

## System Setup

### 1. Environment Variables

Add to your `.env` file:

```bash
# Admin credentials (used with CLI command to create first admin)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=SecureAdminPassword123!

# Other existing configurations...
DATABASE_URL=postgresql://user:password@localhost:5432/naomi_auction
JWT_SECRET_KEY=your-secret-key-here
```

### 2. Create First Admin

After deploying the application, run:

```bash
flask create-admin
```

This will:
- Create a user with email from `ADMIN_EMAIL` environment variable
- Set password from `ADMIN_PASSWORD`
- Set role to `admin` and approved to `true`
- Skip if admin already exists (no duplicates)

**Output:**
```
✓ Admin user created successfully!
  Email: admin@example.com
  Username: admin
  Role: admin
```

---

## User Registration Flow

### Buyer Registration (Instant Approval)

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "role": "buyer",
    "phone": "+1234567890",
    "address": "123 Main St"
  }'
```

**Response:**
```json
{
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "buyer",
    "approved": true,
    "created_at": "2026-02-21T..."
  },
  "message": "Account created successfully"
}
```

✅ Can login immediately

---

### Seller Registration (Pending Approval)

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "seller1",
    "email": "seller@example.com",
    "password": "SecurePass123!",
    "role": "seller",
    "phone": "+1234567890",
    "address": "456 Business Ave"
  }'
```

**Response:**
```json
{
  "data": {
    "id": 2,
    "username": "seller1",
    "email": "seller@example.com",
    "role": "seller",
    "approved": false,
    "created_at": "2026-02-21T..."
  },
  "message": "Seller account created. Awaiting admin approval to enable selling."
}
```

❌ Cannot login until approved

---

### Admin Role Rejection

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "attacker",
    "email": "attacker@example.com",
    "password": "Pass123!",
    "role": "admin"
  }'
```

**Response:**
```json
{
  "error": {
    "message": "Cannot register as admin. Admin accounts must be created by system administrator."
  }
}
```

---

## Login

### Buyer/Admin Login (Instant)

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "role": "buyer",
      "approved": true,
      "created_at": "2026-02-21T..."
    }
  },
  "message": "Login successful"
}
```

---

### Seller Login (Pending Approval)

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "seller1",
    "password": "SecurePass123!"
  }'
```

**Response (BLOCKED):**
```json
{
  "error": {
    "message": "Your seller account is pending admin approval. You will be able to login once approved."
  }
}
```

HTTP Status: **403 Forbidden**

---

## Admin Management

### View Pending Sellers

```bash
curl -X GET http://localhost:5000/api/users/admin/pending-sellers \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Response:**
```json
{
  "data": {
    "pending_sellers": [
      {
        "id": 2,
        "username": "seller1",
        "email": "seller@example.com",
        "role": "seller",
        "approved": false,
        "created_at": "2026-02-21T..."
      }
    ],
    "total": 1,
    "pages": 1,
    "current_page": 1
  }
}
```

---

### Approve Seller

```bash
curl -X POST http://localhost:5000/api/users/admin/sellers/2/approve \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Response:**
```json
{
  "data": {
    "id": 2,
    "username": "seller1",
    "email": "seller@example.com",
    "role": "seller",
    "approved": true,
    "created_at": "2026-02-21T..."
  },
  "message": "Seller \"seller1\" approved successfully"
}
```

✅ Seller can now login and create auctions

---

### Reject Seller

```bash
curl -X POST http://localhost:5000/api/users/admin/sellers/2/reject \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Did not provide business verification"}'
```

**Response:**
```json
{
  "data": {
    "user": {...},
    "reason": "Did not provide business verification"
  },
  "message": "Seller application rejected"
}
```

Seller is reverted to **buyer** role with **approved=true**

---

### Change User Role

```bash
curl -X PUT http://localhost:5000/api/users/admin/users/1/role \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "seller", "approved": true}'
```

---

## CLI Commands

### List All Users

```bash
flask list-users
```

**Output:**
```
ID    Username        Email                     Role       Approved  
----------------------------------------------------------------------
1     admin           admin@example.com         admin      ✓         
2     seller1         seller@example.com        seller     ✗         
3     john_doe        john@example.com          buyer      ✓    

Total: 3 users
```

---

### List Users by Role

```bash
flask list-users --role seller
flask list-users --role admin
```

---

### Update User Role

```bash
flask update-user-role 2 seller --approved
```

**Output:**
```
✓ User role updated successfully
  User: seller1 (ID: 2)
  Old role: buyer
  New role: seller
  Approved: True
```

---

### Approve Seller via CLI

```bash
flask approve-seller 2
```

**Output:**
```
✓ Seller approved successfully
  Username: seller1
  Email: seller@example.com
```

---

## Route Protection Examples

### Seller-Only Endpoint

```python
from app.utils.decorators import seller_required

@my_bp.route('/create-auction', methods=['POST'])
@seller_required
def create_auction(user_id):  # user_id passed automatically
    # Only sellers and admins can access
    return {"message": "Auction created"}
```

---

### Admin-Only Endpoint

```python
from app.utils.decorators import admin_required

@my_bp.route('/admin/settings', methods=['GET'])
@admin_required
def admin_settings(user_id):  # user_id passed automatically
    # Only admins can access
    return {"message": "Admin settings"}
```

---

### Custom Roles Endpoint

```python
from app.utils.decorators import role_required

@my_bp.route('/reports', methods=['GET'])
@role_required('admin')  # Single role as string
def admin_reports(user_id):
    return {"message": "Reports"}

@my_bp.route('/analysis', methods=['GET'])
@role_required(['admin', 'seller'])  # Multiple roles
def analysis(user_id):
    return {"message": "Analysis"}
```

---

## Testing Workflow

### 1. Create First Admin

```bash
# Set environment variables
export ADMIN_EMAIL=admin@test.com
export ADMIN_PASSWORD=AdminPass123!

# Create admin
flask create-admin
```

### 2. Login as Admin

```bash
ADMIN_TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "AdminPass123!"}' \
  | jq -r '.data.access_token')

echo $ADMIN_TOKEN
```

### 3. Register Seller

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "seller_test",
    "email": "seller_test@example.com",
    "password": "SellerPass123!",
    "role": "seller"
  }'
```

### 4. Try to Login (should fail)

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "seller_test", "password": "SellerPass123!"}'
# Returns 403 Forbidden
```

### 5. Admin Approves Seller

```bash
curl -X POST http://localhost:5000/api/users/admin/sellers/2/approve \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 6. Seller Can Now Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "seller_test", "password": "SellerPass123!"}'
# Returns 200 OK with tokens
```

---

## Security Notes

✅ Passwords hashed with Werkzeug
✅ Admin role cannot be registered publicly
✅ Sellers blocked from login until approved
✅ JWT tokens include role claims
✅ Route decorators check both token and role
✅ No duplicate admins created
✅ Seller approval history can be tracked via database

---

## Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(200),
    role VARCHAR(20) NOT NULL DEFAULT 'buyer',  -- buyer, seller, admin
    approved BOOLEAN NOT NULL DEFAULT TRUE,      -- False for unapproved sellers
    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME DEFAULT NOW()
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_approved ON users(approved);
```

---

## Troubleshooting

### "Cannot register as admin"
This is expected! Only system administrators can create admin accounts using the CLI command.

### "Seller account is pending approval"
Admin needs to approve the seller using `/api/users/admin/sellers/<id>/approve` endpoint or CLI command.

### "Invalid token"
Did you include the Bearer token in the Authorization header?
```bash
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### "Admin already exists"
The `flask create-admin` command prevents duplicate admins. Check with `flask list-users --role admin`.
