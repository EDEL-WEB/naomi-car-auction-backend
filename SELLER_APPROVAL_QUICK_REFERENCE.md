# Seller Approval System - Quick Reference Guide

## Quick Start

### 1. Database Migration

Create and run migration:
```bash
# Generate migration file
flask db migrate -m "Add seller approval system"

# Apply migration
flask db upgrade
```

### 2. Run Tests

```bash
# Make script executable (if not already)
chmod +x test_seller_approval.sh

# Run all test scenarios
./test_seller_approval.sh

# Or run with custom base URL
BASE_URL=http://your-server.com ./test_seller_approval.sh
```

---

## Key Components

### Models
- **Seller**: Seller profile with verification status and risk score
- **SellerApprovalLog**: Audit log for all approval decisions

### Service
- **SellerApprovalService**: Handles risk calculation, verification, and approval logic

### Routes
- **POST /api/sellers/register**: Register as seller (requires JWT)
- **POST /api/sellers/{id}/verify-documents**: Verify business documents
- **POST /api/sellers/{id}/verify-email-otp**: Verify email via OTP
- **POST /api/sellers/{id}/verify-phone-otp**: Verify phone via OTP
- **POST /api/sellers/{id}/process-approval**: Process automatic approval
- **POST /api/sellers/{id}/manual-approve**: Admin manual approval
- **POST /api/sellers/{id}/manual-reject**: Admin rejection
- **POST /api/sellers/{id}/suspend**: Admin suspension
- **POST /api/sellers/{id}/flag-suspicious**: Flag suspicious activity
- **GET /api/sellers/{id}**: Get seller profile
- **GET /api/sellers/{id}/logs**: Get approval audit logs

---

## Risk Score System

### Quick Score Calculation

```
Base: 0 points

Add:
  ✓ Documents verified    → +5 points
  ✓ Email verified        → +2 points
  ✓ Phone verified        → +2 points
  ✓ Account 30+ days old  → +1 point
  
Penalties:
  ✗ Suspicious activity   → -5 points
  ✗ 5+ failed logins      → -3 points

Threshold: >= 8 points = AUTO-APPROVED
```

### Score Examples

```
Scenario 1: Safe Seller
  Documents: +5
  Email:     +2
  Phone:     +2
  Account:   +1 (assumed)
  Total:     10 points → AUTO-APPROVED ✓

Scenario 2: Partial Seller
  Documents: +5
  Email:     +2
  Phone:      0 (not verified)
  Account:    0 (new)
  Total:      7 points → MANUAL REVIEW ⚠

Scenario 3: Suspicious Seller
  Documents: +0
  Email:     +0
  Phone:     +0
  Account:    0
  Suspicious: -5
  Total:     -5 points → REJECTED ✗
```

---

## API Response Examples

### Auto-Approved Response
```json
{
    "message": "Seller auto-approved successfully",
    "approved": true,
    "auto_approved": true,
    "seller": {
        "id": 1,
        "is_approved": true,
        "approval_status": "approved",
        "risk_score": 9.0
    }
}
```

### Manual Review Response
```json
{
    "message": "Flagged for manual review. Risk score too low (7.0)/15. Requires manual review.",
    "approved": false,
    "approval_status": "manual_review",
    "seller": {
        "id": 2,
        "is_approved": false,
        "approval_status": "manual_review",
        "risk_score": 7.0
    }
}
```

### Error Response
```json
{
    "error": "Seller not found",
    "status": 404
}
```

---

## Testing Curl Commands

### Get JWT Token
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

### Register as Seller
```bash
curl -X POST http://localhost:5000/api/sellers/register \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Your Company",
    "business_phone": "+1234567890",
    "business_address": "123 Main St",
    "documents": ["url1", "url2"]
  }'
```

### Verify Documents
```bash
curl -X POST http://localhost:5000/api/sellers/1/verify-documents \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_paths": ["url1", "url2"]
  }'
```

### Verify Email OTP
```bash
curl -X POST http://localhost:5000/api/sellers/1/verify-email-otp \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"otp_token": "123456"}'
```

### Verify Phone OTP
```bash
curl -X POST http://localhost:5000/api/sellers/1/verify-phone-otp \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"otp_token": "654321"}'
```

### Process Automatic Approval
```bash
curl -X POST http://localhost:5000/api/sellers/1/process-approval \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### Manual Approve (Admin)
```bash
curl -X POST http://localhost:5000/api/sellers/1/manual-approve \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Verified via phone call"}'
```

### Manual Reject (Admin)
```bash
curl -X POST http://localhost:5000/api/sellers/1/manual-reject \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Documents appear fraudulent"}'
```

### Flag Suspicious Activity (Admin)
```bash
curl -X POST http://localhost:5000/api/sellers/1/flag-suspicious \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Multiple failed payment attempts"}'
```

### Get Seller Profile
```bash
curl -X GET http://localhost:5000/api/sellers/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Approval Logs (Admin)
```bash
curl -X GET "http://localhost:5000/api/sellers/1/logs?limit=50" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

---

## Security Checklist

- [x] JWT authentication for all endpoints
- [x] Role-based authorization (admin-only endpoints)
- [x] Input validation on all requests
- [x] Rate limiting on registration (5 per hour)
- [x] Secure password hashing
- [x] Automated fraud detection via risk scoring
- [x] Comprehensive audit logging
- [x] OTP verification for email/phone
- [x] Document verification mechanism
- [x] Account suspension capability
- [x] Suspicious activity tracking
- [x] SQL injection prevention (SQLAlchemy ORM)
- [x] XSS protection (JSON responses only)
- [x] CORS configured
- [x] Error handling without info leakage

---

## Monitoring

### View Logs
```bash
# Real-time log monitoring (development)
tail -f logs/naomi_auction.log

# Filter approval logs
tail -f logs/naomi_auction.log | grep -i approval

# Filter suspicious activity
tail -f logs/naomi_auction.log | grep -i suspicious

# Filter rejections
tail -f logs/naomi_auction.log | grep -i reject
```

### Database Queries
```sql
-- View all sellers
SELECT * FROM sellers;

-- View pending approvals
SELECT * FROM sellers WHERE approval_status = 'pending';

-- View auto-approved sellers
SELECT * FROM sellers WHERE auto_approved = TRUE;

-- View approval history for a seller
SELECT * FROM seller_approval_logs WHERE seller_id = 1 ORDER BY created_at DESC;

-- View suspicious activities
SELECT * FROM sellers WHERE is_suspended = TRUE;

-- Get approval statistics
SELECT approval_status, COUNT(*) FROM sellers GROUP BY approval_status;
```

---

## Troubleshooting

### Problem: "Seller not found"
**Solution**: Ensure seller_id is correct and seller exists in database

### Problem: "Unauthorized"
**Solution**: Check JWT token is valid and not expired

### Problem: "Admin access required"
**Solution**: Use an admin user's JWT token for admin-only endpoints

### Problem: Risk score not calculated
**Solution**: Ensure all verification endpoints are called before process-approval

### Problem: Documents not verified
**Solution**: Call verify-documents endpoint with valid document paths

### Problem: OTP verification fails
**Solution**: In production, validate against actual OTP service. Mock accepts any 6-char token

---

## Future Enhancements

1. **Real OTP Services**
   - Twilio for SMS OTP
   - SendGrid for email OTP

2. **Document Verification API**
   - OCR document scanning
   - Proof of address validation
   - Identity verification

3. **Machine Learning**
   - Fraud pattern detection
   - Account risk profiling
   - Anomaly detection

4. **Blockchain Integration**
   - Immutable audit trail
   - Public verification record

5. **Geolocation Verification**
   - Location-based fraud detection
   - IP address validation

6. **Behavioral Analytics**
   - Bidding pattern analysis
   - Listing behavior monitoring
   - Transaction history review

---

## Support

For issues or questions:
1. Check logs in `logs/naomi_auction.log`
2. Review database entries in `seller_approval_logs`
3. Verify all required fields in API requests
4. Ensure JWT tokens are valid and not expired
5. Check database connection and migrations

---

## File Structure

```
.
├── app/
│   ├── models/
│   │   └── seller.py (NEW: Seller & SellerApprovalLog)
│   ├── routes/
│   │   └── sellers.py (NEW: Seller management endpoints)
│   └── utils/
│       └── seller_approval_service.py (NEW: Business logic)
├── SELLER_APPROVAL_SYSTEM.md (NEW: Full documentation)
├── SELLER_APPROVAL_QUICK_REFERENCE.md (NEW: This file)
└── test_seller_approval.sh (NEW: Complete test suite)
```

---

## Version History

**v1.0.0** (2026-02-25)
- Initial implementation
- Automatic risk-based approval system
- Manual review and admin overrides
- Complete audit logging
- Test suite with 3 scenarios
