from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from home.models import Product, Order, Category
from django.contrib.auth.models import User
import json


class ReportService:
    """Service for generating various reports"""
    
    @staticmethod
    def get_daily_sales_report(date=None):
        """Generate daily sales report"""
        if date is None:
            date = timezone.now().date()
        
        start_of_day = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        end_of_day = timezone.make_aware(datetime.combine(date, datetime.max.time()))
        
        orders = Order.objects.filter(
            created_at__gte=start_of_day,
            created_at__lte=end_of_day,
            status__in=['completed', 'shipped']
        )
        
        total_sales = orders.count()
        total_revenue = orders.aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0')
        unique_customers = orders.values('user').distinct().count()
        
        # Average order value
        avg_order_value = total_revenue / total_sales if total_sales > 0 else Decimal('0')
        
        # Top 5 products sold today
        top_products = []
        order_items = []
        for order in orders:
            if hasattr(order, 'items'):
                order_items.extend(order.items.all())
        
        product_sales = {}
        for item in order_items:
            if item.product.id not in product_sales:
                product_sales[item.product.id] = {
                    'name': item.product.name,
                    'quantity': 0,
                    'revenue': Decimal('0')
                }
            product_sales[item.product.id]['quantity'] += item.quantity
            product_sales[item.product.id]['revenue'] += item.price * item.quantity
        
        top_products = sorted(
            product_sales.values(),
            key=lambda x: x['revenue'],
            reverse=True
        )[:5]
        
        # Payment method breakdown
        payment_methods = {}
        for order in orders:
            method = order.payment_method if hasattr(order, 'payment_method') else 'Unknown'
            if method not in payment_methods:
                payment_methods[method] = {'count': 0, 'revenue': Decimal('0')}
            payment_methods[method]['count'] += 1
            payment_methods[method]['revenue'] += order.total_price
        
        return {
            'date': str(date),
            'total_sales': total_sales,
            'total_revenue': float(total_revenue),
            'unique_customers': unique_customers,
            'average_order_value': float(avg_order_value),
            'top_products': top_products,
            'payment_methods': {k: {'count': v['count'], 'revenue': float(v['revenue'])} for k, v in payment_methods.items()},
        }
    
    @staticmethod
    def get_order_status_report(date_from=None, date_to=None):
        """Generate order status report"""
        if date_from is None:
            date_from = timezone.now().date() - timedelta(days=30)
        if date_to is None:
            date_to = timezone.now().date()
        
        start_date = timezone.make_aware(datetime.combine(date_from, datetime.min.time()))
        end_date = timezone.make_aware(datetime.combine(date_to, datetime.max.time()))
        
        orders = Order.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
        
        total_orders = orders.count()
        total_revenue = orders.aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0')
        
        status_breakdown = {}
        for status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
            count = orders.filter(status=status).count()
            revenue = orders.filter(status=status).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0')
            percentage = (count / total_orders * 100) if total_orders > 0 else 0
            status_breakdown[status] = {
                'count': count,
                'revenue': float(revenue),
                'percentage': percentage
            }
        
        # Calculate average time in each status (simplified)
        pending_orders = orders.filter(status='pending').count()
        cancelled_orders = orders.filter(status='cancelled').count()
        
        return {
            'date_from': str(date_from),
            'date_to': str(date_to),
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'status_breakdown': status_breakdown,
            'pending_orders': pending_orders,
            'cancelled_orders': cancelled_orders,
            'cancellation_rate': float((cancelled_orders / total_orders * 100) if total_orders > 0 else 0),
        }
    
    @staticmethod
    def get_product_sales_report(date_from=None, date_to=None):
        """Generate product sales report"""
        if date_from is None:
            date_from = timezone.now().date() - timedelta(days=30)
        if date_to is None:
            date_to = timezone.now().date()
        
        start_date = timezone.make_aware(datetime.combine(date_from, datetime.min.time()))
        end_date = timezone.make_aware(datetime.combine(date_to, datetime.max.time()))
        
        orders = Order.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
        
        product_sales = {}
        for order in orders:
            if hasattr(order, 'items'):
                for item in order.items.all():
                    if item.product.id not in product_sales:
                        product_sales[item.product.id] = {
                            'name': item.product.name,
                            'category': item.product.category.name if item.product.category else 'Uncategorized',
                            'units_sold': 0,
                            'revenue': Decimal('0'),
                            'average_price': Decimal('0'),
                        }
                    product_sales[item.product.id]['units_sold'] += item.quantity
                    product_sales[item.product.id]['revenue'] += item.price * item.quantity
        
        # Calculate average price
        for product_id, data in product_sales.items():
            if data['units_sold'] > 0:
                data['average_price'] = float(data['revenue'] / data['units_sold'])
            data['revenue'] = float(data['revenue'])
        
        # Sort by revenue
        sorted_products = sorted(
            product_sales.values(),
            key=lambda x: x['revenue'],
            reverse=True
        )
        
        return {
            'date_from': str(date_from),
            'date_to': str(date_to),
            'total_products_sold': len(product_sales),
            'total_units': sum(p['units_sold'] for p in product_sales.values()),
            'total_revenue': sum(p['revenue'] for p in product_sales.values()),
            'products': sorted_products[:50],  # Top 50 products
        }
    
    @staticmethod
    def get_stock_level_report():
        """Generate stock level report"""
        products = Product.objects.filter(status='active')
        
        low_stock_threshold = 5
        
        total_products = products.count()
        in_stock = products.filter(stock__gt=0).count()
        out_of_stock = products.filter(stock=0).count()
        low_stock = products.filter(stock__gt=0, stock__lte=low_stock_threshold).count()
        
        # Calculate total inventory value
        total_inventory_value = Decimal('0')
        for product in products:
            total_inventory_value += product.price * product.stock
        
        # Low stock items
        low_stock_items = []
        for product in products.filter(stock__lte=low_stock_threshold).order_by('stock'):
            low_stock_items.append({
                'id': product.id,
                'name': product.name,
                'current_stock': product.stock,
                'price': float(product.price),
                'inventory_value': float(product.price * product.stock),
            })
        
        return {
            'total_products': total_products,
            'in_stock': in_stock,
            'out_of_stock': out_of_stock,
            'low_stock': low_stock,
            'low_stock_threshold': low_stock_threshold,
            'total_inventory_value': float(total_inventory_value),
            'low_stock_items': low_stock_items[:20],  # Top 20 low stock items
        }
    
    @staticmethod
    def get_customer_growth_report(date_from=None, date_to=None):
        """Generate customer growth report"""
        if date_from is None:
            date_from = timezone.now().date() - timedelta(days=30)
        if date_to is None:
            date_to = timezone.now().date()
        
        start_date = timezone.make_aware(datetime.combine(date_from, datetime.min.time()))
        end_date = timezone.make_aware(datetime.combine(date_to, datetime.max.time()))
        
        # New customers in period
        new_customers = User.objects.filter(
            date_joined__gte=start_date,
            date_joined__lte=end_date
        ).count()
        
        # Total active customers
        total_customers = User.objects.filter(is_active=True).count()
        
        # Customers who made purchases
        customers_with_orders = Order.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).values('user').distinct().count()
        
        # Repeat customers (made more than 1 purchase)
        repeat_customers = 0
        customer_order_counts = Order.objects.values('user').annotate(order_count=Count('id'))
        for customer_data in customer_order_counts:
            if customer_data['order_count'] > 1:
                repeat_customers += 1
        
        # Average customer lifetime value
        total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0')
        avg_ltv = total_revenue / total_customers if total_customers > 0 else Decimal('0')
        
        # Daily customer growth
        daily_growth = []
        current_date = date_from
        while current_date <= date_to:
            day_start = timezone.make_aware(datetime.combine(current_date, datetime.min.time()))
            day_end = timezone.make_aware(datetime.combine(current_date, datetime.max.time()))
            
            day_new_customers = User.objects.filter(
                date_joined__gte=day_start,
                date_joined__lte=day_end
            ).count()
            
            daily_growth.append({
                'date': str(current_date),
                'new_customers': day_new_customers,
            })
            
            current_date += timedelta(days=1)
        
        return {
            'date_from': str(date_from),
            'date_to': str(date_to),
            'new_customers': new_customers,
            'total_customers': total_customers,
            'customers_with_orders': customers_with_orders,
            'repeat_customers': repeat_customers,
            'average_ltv': float(avg_ltv),
            'daily_growth': daily_growth,
        }
