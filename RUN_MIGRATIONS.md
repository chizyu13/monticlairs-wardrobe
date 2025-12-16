# IMPORTANT: Run Migrations

## New Database Fields Added

The following fields were added to the Order model:
- `cancellation_reason` (TextField) - Stores reason for order cancellation
- `cancelled_by` (ForeignKey to User) - Tracks which admin cancelled the order

## Steps to Apply Changes

### On PythonAnywhere:

```bash
# 1. Pull latest changes
git pull origin main

# 2. Create migrations
python manage.py makemigrations home

# 3. Apply migrations
python manage.py migrate home

# 4. Reload web app
# Click the "Reload" button in PythonAnywhere Web tab
```

### On Local Development:

```bash
# 1. Pull latest changes
git pull origin main

# 2. Create migrations
python manage.py makemigrations home

# 3. Apply migrations
python manage.py migrate home

# 4. Restart development server
python manage.py runserver
```

## What This Fixes

After running migrations:
- Customers will see cancellation reasons when viewing cancelled orders
- Admin can enter cancellation reasons when cancelling orders
- System tracks which admin cancelled each order

## Testing

1. As admin, cancel an order and enter a reason
2. As customer, view the cancelled order details
3. Verify the cancellation reason is displayed in a red alert box
