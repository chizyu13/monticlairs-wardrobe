# Refund System Migration Instructions

## Overview
This implements a cash reversal/refund system for cancelled orders with PIN verification.

## Steps to Deploy

### 1. Create and Run Migrations
```bash
python manage.py makemigrations payment
python manage.py migrate payment
```

### 2. Features Implemented

#### A. Refund Model (`payment/models.py`)
- Tracks all refund requests
- Stores refund status (pending, approved, completed, rejected)
- Records PIN verification
- Links to Payment and Order models

#### B. Admin Views (`custom_admin/views.py`)
- `initiate_refund`: Create refund when order is cancelled
- `refund_detail`: View refund details and process with PIN
- `process_refund`: Verify PIN and complete refund
- `manage_refunds`: List all refunds with filtering

#### C. Automatic Refund Trigger
- When admin changes order status to "cancelled"
- System checks if payment was completed
- Redirects admin to initiate refund

#### D. PIN Verification
- Admin must enter their password as PIN
- Verifies using Django's password hashing
- Prevents unauthorized refunds

### 3. How It Works

1. **Order Cancellation**:
   - Admin changes order status to "Cancelled"
   - System detects completed payment
   - Redirects to refund initiation page

2. **Refund Initiation**:
   - Admin reviews order and payment details
   - Enters reason for refund
   - Creates refund record with "pending" status

3. **Refund Processing**:
   - Admin views refund detail page
   - Enters PIN (their password) to authorize
   - System verifies PIN
   - Marks refund as completed
   - Updates payment status to "cancelled"
   - Updates checkout payment_status to "failed"

4. **Refund Tracking**:
   - All refunds visible in "Manage Refunds" page
   - Filter by status (pending, approved, completed, rejected)
   - View refund history and details

### 4. Security Features
- PIN verification required for refund processing
- Uses Django's secure password hashing
- Audit trail with timestamps and admin user tracking
- Cannot process refund twice (status checks)

### 5. URLs Added
```
/admin/refunds/ - List all refunds
/admin/refunds/<id>/ - View refund details
/admin/refunds/<id>/process/ - Process refund with PIN
/admin/orders/<id>/refund/initiate/ - Initiate refund for order
```

### 6. Testing
1. Create an order and complete payment
2. Change order status to "Cancelled"
3. System should redirect to refund initiation
4. Fill in refund reason and submit
5. On refund detail page, enter admin password as PIN
6. Verify refund is completed and payment status updated

## Notes
- Refunds can only be initiated for cancelled orders with completed payments
- PIN is the admin user's account password
- System tracks who requested and approved each refund
- Refund amount equals the order total price
