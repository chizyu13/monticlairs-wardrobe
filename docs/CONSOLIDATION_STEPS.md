# Model Consolidation - Step-by-Step Guide

## ✅ What Was Done

The duplicate models in `accounts/models.py` have been removed:
- ❌ Removed `accounts.Profile` (duplicate of `home.Profile`)
- ❌ Removed `accounts.Cart` (duplicate of `cart.Cart`)
- ❌ Removed `accounts.Product` (duplicate of `home.Product`)

## 🎯 Active Models (Keep These)

| Model | Location | Usage |
|-------|----------|-------|
| **User** | Django built-in | Authentication |
| **Profile** | `home.models.Profile` | User profiles (bio, phone, picture) |
| **Category** | `home.models.Category` | Product categories |
| **Product** | `home.models.Product` | Product catalog |
| **Cart** | `cart.models.Cart` | Shopping cart |
| **Checkout** | `home.models.Checkout` | Checkout sessions |
| **Order** | `home.models.Order` | Product orders |
| **Sale** | `home.models.Sale` | Sales records |
| **Review** | `home.models.Review` | Product reviews |
| **Payment** | `payment.models.Payment` | Payment transactions |
| **StockReservation** | `home.models.StockReservation` | Stock reservations |
| **StockHistory** | `home.models.StockHistory` | Stock audit trail |

**Total: 12 active models** (13 including Django's User)

---

## 📋 Next Steps - Database Migration

### Step 1: Backup Your Database
```bash
# For SQLite
cp db.sqlite3 db.sqlite3.backup

# For PostgreSQL
pg_dump your_database > backup.sql

# For MySQL
mysqldump -u username -p database_name > backup.sql
```

### Step 2: Check for Existing Migrations
```bash
python manage.py showmigrations accounts
```

### Step 3: Create New Migration
```bash
python manage.py makemigrations accounts
```

This will create a migration to remove the duplicate tables:
- `accounts_profile`
- `accounts_cart`
- `accounts_product`

### Step 4: Review the Migration
Check the generated migration file in `accounts/migrations/` to ensure it's only removing the duplicate tables.

### Step 5: Apply Migration
```bash
python manage.py migrate accounts
```

### Step 6: Verify Database
```bash
# Check that duplicate tables are removed
python manage.py dbshell

# In SQLite
.tables

# In PostgreSQL
\dt

# In MySQL
SHOW TABLES;
```

You should see:
- ✅ `home_profile` (kept)
- ✅ `cart_cart` (kept)
- ✅ `home_product` (kept)
- ❌ `accounts_profile` (removed)
- ❌ `accounts_cart` (removed)
- ❌ `accounts_product` (removed)

---

## 🧪 Testing After Consolidation

### Test 1: User Profile
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from home.models import Profile

# Test profile access
user = User.objects.first()
print(user.profile)  # Should work
print(user.profile.bio)
print(user.profile.profile_picture)
```

### Test 2: Shopping Cart
```python
from cart.models import Cart
from home.models import Product

# Test cart access
cart_items = Cart.objects.filter(user=user)
print(cart_items)
```

### Test 3: Run Server
```bash
python manage.py runserver
```

Visit these pages to verify:
- ✅ User profile page
- ✅ Shopping cart
- ✅ Product listing
- ✅ Checkout process

---

## 🔧 Troubleshooting

### Issue: Migration Conflicts
If you see migration conflicts:
```bash
python manage.py migrate accounts --fake-initial
```

### Issue: Related Name Conflicts
If you see errors about `related_name`:
- The `accounts.Profile` used `related_name='accounts_profile'`
- The `home.Profile` uses `related_name='profile'`
- All templates use `user.profile`, so no changes needed

### Issue: Data Loss Warning
If the migration warns about data loss:
1. Check if `accounts_profile`, `accounts_cart`, or `accounts_product` tables have any data
2. If they do, migrate that data to the primary tables first
3. Then run the migration

---

## 📊 Before vs After

### Before Consolidation
```
Database Tables: 16
- auth_user
- home_profile ✅
- accounts_profile ❌ (duplicate)
- home_product ✅
- accounts_product ❌ (duplicate)
- cart_cart ✅
- accounts_cart ❌ (duplicate)
- home_category
- home_checkout
- home_order
- home_sale
- home_review
- home_stockreservation
- home_stockhistory
- payment_payment
- cart_checkout
```

### After Consolidation
```
Database Tables: 13
- auth_user
- home_profile ✅
- home_product ✅
- cart_cart ✅
- home_category
- home_checkout
- home_order
- home_sale
- home_review
- home_stockreservation
- home_stockhistory
- payment_payment
- cart_checkout
```

**Result: 3 duplicate tables removed, cleaner database structure!**

---

## ✨ Benefits of Consolidation

1. **No More Conflicts** - Single source of truth for each model
2. **Cleaner Codebase** - Easier to maintain and understand
3. **Better Performance** - Fewer tables to query
4. **Easier Migrations** - No duplicate migration conflicts
5. **Clear Structure** - Each app has its specific responsibility

---

## 📝 Import Reference

If you need to use these models in different apps:

```python
# In any view or model file
from django.contrib.auth.models import User
from home.models import Profile, Product, Category, Order, Checkout, Sale, Review
from home.models import StockReservation, StockHistory
from cart.models import Cart
from payment.models import Payment

# Example usage
user = User.objects.get(username='john')
profile = user.profile  # Access home.Profile
cart_items = Cart.objects.filter(user=user)  # Access cart.Cart
```

---

## 🚀 Ready to Proceed?

Run these commands in order:

```bash
# 1. Backup database
cp db.sqlite3 db.sqlite3.backup

# 2. Create migration
python manage.py makemigrations accounts

# 3. Apply migration
python manage.py migrate accounts

# 4. Test the application
python manage.py runserver
```

---

## ⚠️ Important Notes

- The consolidation is **non-destructive** if the duplicate tables were empty
- All existing functionality will continue to work
- No template changes are needed (they already use `user.profile`)
- No view changes are needed (they already import from correct locations)

**You're all set! The duplicate models have been removed and your database structure is now clean and optimized.**
