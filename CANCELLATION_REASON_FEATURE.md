# Order Cancellation Reason Feature

## Overview
Added the ability for admins to provide cancellation reasons that are visible to customers when their orders are cancelled or fail.

## Changes Made

### 1. Database Changes (`home/models.py`)
Added two new fields to the Order model:
- `cancellation_reason` (TextField): Stores the reason for cancellation/failure
- `cancelled_by` (ForeignKey to User): Tracks which admin cancelled the order

### 2. Admin Interface (`custom_admin/views.py`)
- Modified `update_order_status` to capture cancellation reason from POST data
- Saves the reason and admin user when order status is changed to "cancelled"

### 3. Admin Template (`custom_admin/templates/custom_admin/order_detail.html`)
- Added textarea field that appears when admin selects "Cancelled" status
- Field is required when cancelling an order
- JavaScript shows/hides the reason field based on status selection
- Placeholder text guides admin to enter customer-visible reason

### 4. Customer Interface (`home/templates/home/checkout_detail.html`)
- Added cancellation notice alert box that displays when order is cancelled
- Shows the cancellation reason provided by admin
- Displays which admin cancelled the order
- Styled with red theme to indicate cancellation

## How It Works

### Admin Workflow:
1. Admin views order detail page
2. Selects "Cancelled" from status dropdown
3. Textarea appears asking for cancellation reason
4. Admin enters reason (e.g., "Product out of stock", "Payment verification failed")
5. Clicks "Update Status"
6. Reason is saved with order

### Customer Experience:
1. Customer views their order details
2. If order is cancelled, sees red "Cancelled" badge
3. Below the header, sees a red alert box with:
   - "Order Cancellation Notice" heading
   - The reason provided by admin
   - Which admin cancelled it (optional)

## Migration Required

Run these commands on PythonAnywhere:

```bash
python manage.py makemigrations home
python manage.py migrate home
```

## Benefits

1. **Transparency**: Customers know why their order was cancelled
2. **Customer Service**: Reduces support inquiries about cancellations
3. **Trust**: Shows professionalism and clear communication
4. **Accountability**: Tracks which admin cancelled orders

## Example Reasons

Common cancellation reasons admins might enter:
- "Product is currently out of stock"
- "Payment verification failed - please contact support"
- "Unable to deliver to specified location"
- "Customer requested cancellation"
- "Duplicate order detected"
- "Fraudulent activity suspected"

## UI Screenshots

### Admin Side:
- Status dropdown with "Cancelled" option
- Textarea field for entering reason (required)
- "Update Status" button

### Customer Side:
- Red "Cancelled" status badge
- Red alert box with cancellation notice
- Reason text clearly displayed
- Admin name who cancelled (for accountability)
