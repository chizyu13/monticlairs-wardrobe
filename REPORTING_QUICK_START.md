# Reporting System - Quick Start Guide

## 🚀 Getting Started

### Step 1: Access Reports
1. Login to your admin account
2. Go to Admin Dashboard: `http://localhost:8000/accounts/admin-dashboard/`
3. Click the **"Reports"** button in Quick Actions

### Step 2: View Available Reports
You'll see 5 essential reports:
- 📊 Daily Sales Report
- 📦 Order Status Report
- 🛍️ Product Sales Report
- 📦 Stock Level Report
- 👥 Customer Growth Report

### Step 3: Generate a Report
Click on any report to view it. For example:
- **Daily Sales Report**: Shows today's sales by default
- **Order Status Report**: Shows last 30 days by default
- **Stock Level Report**: Shows current inventory status

### Step 4: Filter Data (Optional)
Most reports allow date filtering:
- Select "From Date" and "To Date"
- Click "Generate Report"

### Step 5: Export Report
Each report has export options:
- **Export CSV** - Download as spreadsheet
- **Export PDF** - Download as formatted document

---

## 📊 What Each Report Shows

### Daily Sales Report
```
✓ Total Sales Count
✓ Total Revenue
✓ Unique Customers
✓ Average Order Value
✓ Top 5 Products Sold
✓ Payment Method Breakdown
```

### Order Status Report
```
✓ Total Orders
✓ Total Revenue
✓ Orders by Status (Pending, Processing, Shipped, Delivered, Cancelled)
✓ Pending Orders Count
✓ Cancellation Rate
```

### Product Sales Report
```
✓ Total Products Sold
✓ Total Units Sold
✓ Total Revenue
✓ Top 50 Products with Details
✓ Revenue per Product
✓ Average Price per Product
```

### Stock Level Report
```
✓ Total Products
✓ In Stock Count
✓ Out of Stock Count
✓ Low Stock Count
✓ Total Inventory Value
✓ Low Stock Items List
```

### Customer Growth Report
```
✓ New Customers
✓ Total Active Customers
✓ Customers with Orders
✓ Repeat Customers
✓ Average Customer Lifetime Value
✓ Daily Growth Data
```

---

## 🔗 Direct URLs

Access reports directly via URLs:

```
Reports Dashboard:
http://localhost:8000/reports/

Daily Sales Report:
http://localhost:8000/reports/daily-sales/

Order Status Report:
http://localhost:8000/reports/order-status/

Product Sales Report:
http://localhost:8000/reports/product-sales/

Stock Level Report:
http://localhost:8000/reports/stock-level/

Customer Growth Report:
http://localhost:8000/reports/customer-growth/
```

---

## 💾 Exporting Reports

### Export to CSV
```
http://localhost:8000/reports/export/?type=daily_sales&format=csv&date=2025-12-15
```

### Export to PDF
```
http://localhost:8000/reports/export/?type=daily_sales&format=pdf&date=2025-12-15
```

---

## 🔐 Access Requirements

- ✅ Must be logged in as admin (superuser)
- ✅ Only superusers can access reports
- ✅ All access is logged for audit purposes

---

## 📝 Common Tasks

### View Today's Sales
1. Go to `/reports/daily-sales/`
2. Report shows today's data by default
3. Click "Export CSV" or "Export PDF" to download

### Check Inventory Status
1. Go to `/reports/stock-level/`
2. View low stock items
3. See total inventory value
4. Export for records

### Analyze Product Performance
1. Go to `/reports/product-sales/`
2. Set date range (e.g., last 30 days)
3. Click "Generate Report"
4. View top performing products
5. Export for analysis

### Monitor Order Fulfillment
1. Go to `/reports/order-status/`
2. Set date range
3. View orders by status
4. Check cancellation rate
5. Export for records

### Track Customer Growth
1. Go to `/reports/customer-growth/`
2. Set date range
3. View new customers and retention
4. Check customer lifetime value
5. Export for analysis

---

## 🎯 Tips & Tricks

### Tip 1: Date Filtering
- Most reports support date range filtering
- Use "From Date" and "To Date" fields
- Click "Generate Report" to apply filters

### Tip 2: Export for Sharing
- Export reports as CSV for spreadsheet analysis
- Export as PDF for professional presentations
- Share exported files with team members

### Tip 3: Regular Monitoring
- Check Daily Sales Report every morning
- Monitor Stock Level Report weekly
- Review Customer Growth Report monthly

### Tip 4: Audit Trail
- All report access is logged
- View access logs in Django admin
- Track who accessed which reports

---

## ❓ FAQ

**Q: Can I schedule reports to be sent automatically?**  
A: This feature is planned for Phase 2. Currently, you can export and share manually.

**Q: Can I create custom reports?**  
A: Custom report builder is planned for Phase 3. Currently, 5 essential reports are available.

**Q: How often is data updated?**  
A: Reports show real-time data. Data is generated when you view the report.

**Q: Can non-admin users access reports?**  
A: No, only superusers (admins) can access reports for security reasons.

**Q: How do I export a report?**  
A: Click "Export CSV" or "Export PDF" button on any report page.

---

## 🆘 Troubleshooting

### Issue: "Permission Denied" when accessing reports
**Solution:** Make sure you're logged in as a superuser (admin)

### Issue: No data showing in reports
**Solution:** Check if you have orders/products in your database

### Issue: Export button not working
**Solution:** Make sure reportlab is installed: `pip install reportlab`

### Issue: Date filtering not working
**Solution:** Use YYYY-MM-DD format for dates

---

## 📞 Support

For more information, see:
- `REPORTING_SYSTEM_SUMMARY.md` - Complete summary
- `docs/REPORTING_SYSTEM_SPECIFICATION.md` - Full specification
- `docs/REPORTING_SYSTEM_IMPLEMENTATION.md` - Technical details

---

**Happy Reporting! 📊**
