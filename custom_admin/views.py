from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from home.models import Order
from accounts.models import Product

# Admin check function to ensure only admins can access
def is_admin(user):
    return user.is_staff or user.is_superuser

# Apply login_required and user_passes_test decorators to restrict access to admins
@login_required
@user_passes_test(is_admin)
def custom_admin_dashboard(request):
    # Get stats
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    # Assuming you might want to include revenue in the future
    # total_revenue = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        # 'total_revenue': total_revenue,  # Uncomment when Payment model is available
    }

    return render(request, 'custom_admin/dashboard.html', context)

# Manage Users View
@login_required
@user_passes_test(is_admin)
def manage_users(request):
    users = User.objects.all()
    return render(request, 'custom_admin/manage_users.html', {'users': users})

# Sales Reports View
@login_required
@user_passes_test(is_admin)
def sales_reports(request):
    orders = Order.objects.all()
    total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    return render(request, 'custom_admin/sales_reports.html', {'orders': orders, 'total_sales': total_sales})

from django.shortcuts import render

# Assuming you want to list users or manage them in some way
def manage_users(request):
    # You can query users or perform any logic needed
    users = User.objects.all()  # Or your custom user model
    return render(request, 'custom_admin/manage_users.html', {'users': users})
