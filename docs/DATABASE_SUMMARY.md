# Montclair Wardrobe - Database Summary

## 📊 Final Database Structure

After consolidation, your system has **13 database tables** (12 custom + 1 Django User table).

---

## 🗂️ Complete Table List

| # | Table Name | App | Description | Key Fields |
|---|------------|-----|-------------|------------|
| 1 | **auth_user** | Django | User authentication | username, email, password, is_staff |
| 2 | **home_profile** | home | User profiles | user_id, bio, location, phone_number, profile_picture |
| 3 | **home_category** | home | Product categories | name, description, created_by |
| 4 | **home_product** | home | Product catalog | name, price, seller, category, stock, status, approval_status |
| 5 | **home_order** | home | Product orders | user, product, quantity, total_price, status, checkout |
| 6 | **home_checkout** | home | Checkout sessions | user, location, payment_method, delivery_fee, payment_status |
| 7 | **home_sale** | home | Sales records | product, seller, buyer, total_amount, quantity |
| 8 | **home_review** | home | Product reviews | product, user, rating, title, comment, is_verified_purchase |
| 9 | **home_stockreservation** | home | Stock reservations | user, product, quantity, status, expires_at |
| 10 | **home_stockhistory** | home | Stock audit trail | product, change_type, quantity_change, stock_before, stock_after |
| 11 | **cart_cart** | cart | Shopping cart | user, product, quantity, added_at |
| 12 | **cart_checkout** | cart | Cart checkouts | user, location, payment_method, delivery_fee |
| 13 | **payment_payment** | payment | Payment transactions | user, method, amount, reference, status |

---

## 📈 Database Statistics

### By App
- **home**: 8 tables (core business logic)
- **cart**: 2 tables (shopping cart)
- **payment**: 1 table (payment processing)
- **accounts**: 0 tables (duplicates removed)
- **Django**: 1 table (user authentication)

### By Category
- **User Management**: 2 tables (User, Profile)
- **Product Management**: 4 tables (Category, Product, Review, Sale)
- **Shopping**: 2 tables (Cart, cart.Checkout)
- **Orders**: 2 tables (Order, home.Checkout)
- **Inventory**: 2 tables (StockReservation, StockHistory)
- **Payment**: 1 table (Payment)

---

## 🔗 Key Relationships

### One-to-One
- User ↔ Profile

### One-to-Many
- User → Products (as seller)
- User → Orders
- User → Checkouts
- User → Cart Items
- User → Reviews
- User → Payments
- User → Stock Reservations
- Category → Products
- Product → Orders
- Product → Reviews
- Product → Cart Items
- Product → Stock Reservations
- Product → Stock History
- Checkout → Orders

### Many-to-Many (through intermediary)
- User ↔ Product (through Cart)
- User ↔ Product (through Order)
- User ↔ Product (through Review)

---

## 💾 Storage Estimates

### Approximate Row Sizes
| Table | Avg Size per Row | Notes |
|-------|------------------|-------|
| User | ~500 bytes | Includes hashed password |
| Profile | ~2-5 KB | Includes profile picture path |
| Product | ~3-10 KB | Includes image path |
| Order | ~200 bytes | Transactional data |
| Cart | ~150 bytes | Temporary data |
| Review | ~1-2 KB | Text content |
| Payment | ~300 bytes | Transaction records |
| StockHistory | ~200 bytes | Audit logs |

### Growth Projections
For 1,000 active users:
- **Users & Profiles**: ~5 MB
- **Products** (500 products): ~5 MB
- **Orders** (10,000 orders): ~2 MB
- **Reviews** (2,000 reviews): ~4 MB
- **Stock History** (50,000 records): ~10 MB
- **Total**: ~26 MB (excluding images)

---

## 🔍 Indexes

### Performance Indexes
```sql
-- Product indexes
CREATE INDEX idx_product_seller_status ON home_product(seller_id, status);
CREATE INDEX idx_product_created ON home_product(created_at);

-- Order indexes
CREATE INDEX idx_order_created ON home_order(created_at);

-- Review indexes
CREATE INDEX idx_review_product_rating ON home_review(product_id, rating);
CREATE INDEX idx_review_created ON home_review(created_at);

-- Payment indexes
CREATE INDEX idx_payment_user_status ON payment_payment(user_id, status);
CREATE INDEX idx_payment_reference ON payment_payment(reference);
CREATE INDEX idx_payment_created ON payment_payment(created_at);

-- Stock Reservation indexes
CREATE INDEX idx_reservation_user_status ON home_stockreservation(user_id, status);
CREATE INDEX idx_reservation_product_status ON home_stockreservation(product_id, status);
CREATE INDEX idx_reservation_expires ON home_stockreservation(expires_at, status);

-- Stock History indexes
CREATE INDEX idx_history_product_created ON home_stockhistory(product_id, created_at);
CREATE INDEX idx_history_type_created ON home_stockhistory(change_type, created_at);
CREATE INDEX idx_history_user_created ON home_stockhistory(changed_by_id, created_at);
```

---

## 🎯 Unique Constraints

| Table | Constraint | Fields |
|-------|------------|--------|
| Category | Unique name | name |
| Review | One review per user per product | (product_id, user_id) |
| Cart | One cart item per user per product | (user_id, product_id) |
| Payment | Unique reference | reference |

---

## 📝 Status Enumerations

### Product Status
- `active` - Available for purchase
- `inactive` - Not available
- `sold` - Sold out
- `draft` - Not published

### Product Approval Status
- `pending` - Awaiting approval
- `approved` - Approved for sale
- `rejected` - Rejected

### Order Status
- `pending` - Order placed
- `processing` - Being prepared
- `shipped` - Shipped
- `delivered` - Delivered
- `cancelled` - Cancelled

### Payment Status
- `pending` - Initiated
- `processing` - Processing
- `completed` - Successful
- `failed` - Failed
- `cancelled` - Cancelled

### Stock Reservation Status
- `active` - Active reservation
- `completed` - Order placed
- `expired` - Time expired
- `cancelled` - Cancelled

---

## 🔐 Data Validation

### Phone Numbers
- Format: `+260XXXXXXXXX` (Zambian format)
- Validated using RegexValidator

### Prices
- Minimum: 0.01 (no zero or negative prices)
- Decimal: 10 digits, 2 decimal places

### Stock
- Positive integers only
- Automatic reduction on order creation
- Reservation system prevents overselling

### Reviews
- Rating: 1-5 stars
- One review per user per product
- Verified purchase badge

---

## 🚀 Performance Optimization

### Query Optimization
1. **Select Related**: Use for foreign key lookups
   ```python
   Order.objects.select_related('user', 'product', 'checkout')
   ```

2. **Prefetch Related**: Use for reverse foreign keys
   ```python
   Product.objects.prefetch_related('reviews', 'orders')
   ```

3. **Only/Defer**: Load only needed fields
   ```python
   Product.objects.only('name', 'price', 'stock')
   ```

### Caching Strategy
- Cache product catalog (15 minutes)
- Cache category list (30 minutes)
- Cache user profile (5 minutes)
- Don't cache: Cart, Orders, Stock levels

---

## 📊 Reporting Queries

### Sales Report
```python
from django.db.models import Sum, Count
from home.models import Sale

# Total sales by seller
sales_by_seller = Sale.objects.values('seller__username').annotate(
    total_sales=Sum('total_amount'),
    order_count=Count('id')
)
```

### Stock Report
```python
from home.models import Product

# Low stock products
low_stock = Product.objects.filter(
    stock__lte=5,
    stock__gt=0,
    status='active'
)
```

### Popular Products
```python
from django.db.models import Avg, Count
from home.models import Product

# Top rated products
top_products = Product.objects.annotate(
    avg_rating=Avg('reviews__rating'),
    review_count=Count('reviews')
).filter(review_count__gte=5).order_by('-avg_rating')
```

---

## 🛡️ Data Integrity

### Automatic Actions
- **On Order Create**: Reduce product stock
- **On Order Cancel**: Restore product stock
- **On Reservation Expire**: Release reserved stock
- **On Profile Create**: Auto-create for new users
- **On Stock Change**: Log to StockHistory

### Cascade Deletes
- Delete User → Delete Profile, Orders, Cart, Reviews
- Delete Product → Delete Orders, Reviews, Cart items
- Delete Checkout → Set Order.checkout to NULL

---

## 📅 Maintenance Tasks

### Daily
- Clean up expired stock reservations
- Process pending payments

### Weekly
- Archive old stock history (>90 days)
- Generate sales reports

### Monthly
- Database backup
- Index optimization
- Query performance analysis

---

## ✅ Database Health Checklist

- [x] No duplicate models
- [x] All foreign keys have indexes
- [x] Unique constraints in place
- [x] Proper cascade rules
- [x] Validation at model level
- [x] Audit trail for stock changes
- [x] Soft deletes where needed
- [x] Timestamps on all tables

---

**Your database is now clean, optimized, and ready for production! 🎉**
