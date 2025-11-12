# Model Consolidation Plan

## Issue
Your system has duplicate models that can cause database conflicts:
1. **Profile model** exists in both `home` and `accounts` apps
2. **Cart model** exists in both `cart` and `accounts` apps

## Current Usage Analysis

### Profile Models
- ✅ **home.Profile** - ACTIVE (used in 10+ templates and views)
- ❌ **accounts.Profile** - DUPLICATE (not imported anywhere)

### Cart Models
- ✅ **cart.Cart** - ACTIVE (imported in home/views.py and custom_admin/views.py)
- ❌ **accounts.Cart** - DUPLICATE (not imported anywhere)

## Consolidation Strategy

### Step 1: Remove Duplicate Models from accounts/models.py
Remove the duplicate Profile and Cart models from the accounts app.

### Step 2: Keep Active Models
- Keep `home.Profile` (primary profile model)
- Keep `cart.Cart` (primary cart model)

### Step 3: Clean Up Database
After removing duplicates, create and run migrations to clean up any orphaned tables.

## Implementation Steps

1. ✅ Backup your database
2. ✅ Update accounts/models.py to remove duplicates
3. ✅ Create migrations
4. ✅ Run migrations
5. ✅ Test the application

## Files to Update
- `accounts/models.py` - Remove duplicate models
