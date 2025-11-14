from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.core.paginator import Paginator
from home.models import Order, Product, Category, Sale, Checkout
from payment.models import Payment
from cart.models import Cart
from home.forms import ProductForm


# --- Helper Function ---
def is_admin(user):
    """Ensure only staff or superusers can access admin pages."""
    return user.is_staff or user.is_superuser


# --- Dashboard View ---
@login_required
@user_passes_test(is_admin)
def custom_admin_dashboard(request):
    total_users = User.objects.count()
    total_products = Product.objects.count()
    approved_products = Product.objects.filter(approval_status='approved').count()
    pending_products = Product.objects.filter(approval_status='pending').count()
    total_orders = Order.objects.count()
    
    context = {
        'total_users': total_users,
        'total_products': total_products,
        'approved_products': approved_products,
        'pending_products': pending_products,
        'total_orders': total_orders,
    }

    return render(request, 'custom_admin/dashboard.html', context)


# --- Manage Users ---
@login_required
@user_passes_test(is_admin)
def manage_users(request):
    users = User.objects.all()
    return render(request, 'custom_admin/manage_users.html', {'users': users})


# --- Sales Reports ---
@login_required
@user_passes_test(is_admin)
def sales_reports(request):
    """
    Displays either Sale or Order data depending on availability.
    Uses total_price instead of total_amount to prevent FieldError.
    """
    from datetime import datetime, timedelta
    from django.db.models.functions import TruncDate
    import json
    
    # Get filter parameters
    date_range = int(request.GET.get('date_range', 30))
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    
    # Get all categories for filter dropdown
    categories = Category.objects.all()
    
    try:
        from home.models import Sale as SaleModel
        sales = SaleModel.objects.all()
        
        # Apply filters
        end_date = timezone.now()
        start_date = end_date - timedelta(days=date_range)
        sales = sales.filter(sale_date__gte=start_date)
        
        if category_filter:
            sales = sales.filter(product__category_id=category_filter)
        
        sales = sales.order_by('-sale_date')

        # ✅ FIXED: Use total_amount for Sale model
        total_sales = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        sales_count = sales.count()
        average_sale = (total_sales / sales_count) if sales_count > 0 else 0

        # Get sales trend data
        start_date = end_date - timedelta(days=date_range)
        
        daily_sales = sales.filter(sale_date__gte=start_date).annotate(
            date=TruncDate('sale_date')
        ).values('date').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('date')
        
        # Prepare chart data
        chart_labels = [item['date'].strftime('%b %d') for item in daily_sales]
        chart_data = [float(item['total']) for item in daily_sales]
        
        # Get category distribution
        category_sales = sales.values('product__category__name').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total')[:5]
        
        category_labels = [item['product__category__name'] or 'Uncategorized' for item in category_sales]
        category_data = [float(item['total']) for item in category_sales]

        context = {
            'orders': sales,
            'total_sales': total_sales,
            'sales_count': sales_count,
            'average_sale': average_sale,
            'data_type': 'sales',
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
            'category_labels': json.dumps(category_labels),
            'category_data': json.dumps(category_data),
            'categories': categories,
        }

    except Exception as e:
        # Fallback to Order model if Sale model has issues
        orders = Order.objects.all()
        
        # Apply filters
        end_date = timezone.now()
        start_date = end_date - timedelta(days=date_range)
        orders = orders.filter(created_at__gte=start_date)
        
        if category_filter:
            orders = orders.filter(product__category_id=category_filter)
        
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        orders = orders.order_by('-created_at')
        
        total_sales = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        orders_count = orders.count()
        average_order = (total_sales / orders_count) if orders_count > 0 else 0
        
        # Get sales trend data
        start_date = end_date - timedelta(days=date_range)
        
        daily_sales = orders.filter(created_at__gte=start_date).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total=Sum('total_price'),
            count=Count('id')
        ).order_by('date')
        
        # Prepare chart data
        chart_labels = [item['date'].strftime('%b %d') for item in daily_sales]
        chart_data = [float(item['total']) for item in daily_sales]
        
        # Get category distribution
        category_sales = orders.values('product__category__name').annotate(
            total=Sum('total_price'),
            count=Count('id')
        ).order_by('-total')[:5]
        
        category_labels = [item['product__category__name'] or 'Uncategorized' for item in category_sales]
        category_data = [float(item['total']) for item in category_sales]

        context = {
            'orders': orders,
            'total_sales': total_sales,
            'sales_count': orders_count,
            'average_sale': average_order,
            'data_type': 'orders',
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
            'category_labels': json.dumps(category_labels),
            'category_data': json.dumps(category_data),
            'categories': categories,
        }

    return render(request, 'custom_admin/sales_reports.html', context)


@login_required
@user_passes_test(is_admin)
def export_sales_report(request):
    """Export sales report as CSV"""
    import csv
    from datetime import timedelta
    
    # Get filter parameters
    date_range = int(request.GET.get('date_range', 30))
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Customer', 'Product', 'Quantity', 'Amount', 'Status', 'Date'])
    
    try:
        from home.models import Sale as SaleModel
        sales = SaleModel.objects.all()
        
        # Apply filters
        end_date = timezone.now()
        start_date = end_date - timedelta(days=date_range)
        sales = sales.filter(sale_date__gte=start_date)
        
        if category_filter:
            sales = sales.filter(product__category_id=category_filter)
        
        sales = sales.order_by('-sale_date')
        
        for sale in sales:
            writer.writerow([
                sale.id,
                sale.buyer.get_full_name() or sale.buyer.username,
                sale.product.name,
                sale.quantity,
                f"ZMW {sale.total_amount}",
                'Completed',
                sale.sale_date.strftime('%Y-%m-%d %H:%M')
            ])
    
    except:
        # Fallback to Order model
        orders = Order.objects.all()
        
        # Apply filters
        end_date = timezone.now()
        start_date = end_date - timedelta(days=date_range)
        orders = orders.filter(created_at__gte=start_date)
        
        if category_filter:
            orders = orders.filter(product__category_id=category_filter)
        
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        orders = orders.order_by('-created_at')
        
        for order in orders:
            writer.writerow([
                order.id,
                order.user.get_full_name() or order.user.username,
                order.product.name,
                order.quantity,
                f"ZMW {order.total_price}",
                order.get_status_display(),
                order.created_at.strftime('%Y-%m-%d %H:%M')
            ])
    
    return response


# --- Product Management ---
@login_required
@user_passes_test(is_admin)
def manage_products(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/manage_products.html', {'products': products})


@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user  # Admin as seller
            product.approval_status = 'approved'  # Auto-approved for admin
            product.approved_by = request.user
            product.approved_at = timezone.now()
            product.save()
            messages.success(request, f'Product "{product.name}" has been added successfully!')
            return redirect('custom_admin:manage_products')
    else:
        form = ProductForm()
    return render(request, 'custom_admin/add_product.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def approve_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.approval_status = 'approved'
    product.approved_by = request.user
    product.approved_at = timezone.now()
    product.save()
    messages.success(request, f'Product "{product.name}" has been approved!')
    return redirect('custom_admin:manage_products')


@login_required
@user_passes_test(is_admin)
def reject_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.approval_status = 'rejected'
    product.save()
    messages.warning(request, f'Product "{product.name}" has been rejected!')
    return redirect('custom_admin:manage_products')


@login_required
@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_name = product.name
    product.delete()
    messages.success(request, f'Product "{product_name}" has been deleted!')
    return redirect('custom_admin:manage_products')


# --- Order Management ---
@login_required
@user_passes_test(is_admin)
def manage_orders(request):
    """Manage all customer orders"""
    orders = Order.objects.select_related('user', 'product', 'checkout').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    # Get status choices for filter
    status_choices = Order.StatusChoices.choices
    
    context = {
        'orders': orders,
        'status_choices': status_choices,
        'current_status': status_filter
    }
    return render(request, 'custom_admin/manage_orders.html', context)


@login_required
@user_passes_test(is_admin)
def order_detail(request, order_id):
    """View detailed order information"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'custom_admin/order_detail.html', {'order': order})


@login_required
@user_passes_test(is_admin)
def update_order_status(request, order_id):
    """Update order status"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.StatusChoices.choices):
            old_status = order.status
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated from {old_status} to {new_status}')
        else:
            messages.error(request, 'Invalid status selected')
    
    return redirect('custom_admin:order_detail', order_id=order_id)


# --- Customer Management ---
@login_required
@user_passes_test(is_admin)
def manage_customers(request):
    """Manage customer accounts and activity"""
    customers = User.objects.filter(is_staff=False, is_superuser=False).annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__total_price')
    ).order_by('-date_joined')
    
    paginator = Paginator(customers, 20)
    page_number = request.GET.get('page')
    customers = paginator.get_page(page_number)
    
    return render(request, 'custom_admin/manage_customers.html', {'customers': customers})


@login_required
@user_passes_test(is_admin)
def customer_detail(request, user_id):
    """View detailed customer information"""
    customer = get_object_or_404(User, id=user_id, is_staff=False)
    orders = Order.objects.filter(user=customer).select_related('product', 'checkout').order_by('-created_at')[:10]
    
    # Customer statistics
    total_orders = Order.objects.filter(user=customer).count()
    total_spent = Order.objects.filter(user=customer).aggregate(Sum('total_price'))['total_price__sum'] or 0
    average_order = (total_spent / total_orders) if total_orders > 0 else 0
    
    context = {
        'customer': customer,
        'orders': orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'average_order': average_order
    }
    return render(request, 'custom_admin/customer_detail.html', context)


# --- Dashboard Analytics ---
@login_required
@user_passes_test(is_admin)
def analytics_dashboard(request):
    """Advanced analytics dashboard"""
    from django.db.models import Q
    from datetime import datetime, timedelta
    
    # Date range (last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Order statistics
    total_orders = Order.objects.count()
    recent_orders = Order.objects.filter(created_at__gte=start_date).count()
    pending_orders = Order.objects.filter(status='pending').count()
    completed_orders = Order.objects.filter(status='delivered').count()
    
    # Revenue statistics
    total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    recent_revenue = Order.objects.filter(created_at__gte=start_date).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Product statistics
    total_products = Product.objects.count()
    active_products = Product.objects.filter(status='active', approval_status='approved').count()
    pending_products = Product.objects.filter(approval_status='pending').count()
    
    # Customer statistics
    total_customers = User.objects.filter(is_staff=False, is_superuser=False).count()
    recent_customers = User.objects.filter(is_staff=False, is_superuser=False, date_joined__gte=start_date).count()
    
    # Top selling products
    top_products = Product.objects.annotate(
        total_sold=Sum('orders__quantity')
    ).filter(total_sold__gt=0).order_by('-total_sold')[:5]
    
    context = {
        'total_orders': total_orders,
        'recent_orders': recent_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
        'recent_revenue': recent_revenue,
        'total_products': total_products,
        'active_products': active_products,
        'pending_products': pending_products,
        'total_customers': total_customers,
        'recent_customers': recent_customers,
        'top_products': top_products,
    }
    return render(request, 'custom_admin/analytics.html', context)


# --- Payment Verification ---
@login_required
@user_passes_test(is_admin)
def manage_payments(request):
    """Manage and verify customer payments"""
    # Get filter parameters
    status_filter = request.GET.get('status', 'pending')
    method_filter = request.GET.get('method', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    payments = Payment.objects.select_related('user').order_by('-created_at')
    
    # Apply filters
    if status_filter and status_filter != 'all':
        payments = payments.filter(status=status_filter)
    
    if method_filter:
        payments = payments.filter(method=method_filter)
    
    if search_query:
        payments = payments.filter(
            Q(reference__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    # Get counts for each status
    pending_count = Payment.objects.filter(status='pending').count()
    processing_count = Payment.objects.filter(status='processing').count()
    completed_count = Payment.objects.filter(status='completed').count()
    failed_count = Payment.objects.filter(status='failed').count()
    
    # Pagination
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    payments = paginator.get_page(page_number)
    
    context = {
        'payments': payments,
        'status_filter': status_filter,
        'method_filter': method_filter,
        'search_query': search_query,
        'pending_count': pending_count,
        'processing_count': processing_count,
        'completed_count': completed_count,
        'failed_count': failed_count,
        'payment_methods': Payment.PAYMENT_METHODS,
        'status_choices': Payment.STATUS_CHOICES,
    }
    return render(request, 'custom_admin/manage_payments.html', context)


@login_required
@user_passes_test(is_admin)
def payment_detail(request, payment_id):
    """View detailed payment information"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Get related checkout if exists
    checkout = Checkout.objects.filter(
        user=payment.user,
        transaction_id=payment.reference
    ).first()
    
    # Get related orders
    orders = []
    if checkout:
        orders = Order.objects.filter(checkout=checkout).select_related('product')
    
    context = {
        'payment': payment,
        'checkout': checkout,
        'orders': orders,
    }
    return render(request, 'custom_admin/payment_detail.html', context)


@login_required
@user_passes_test(is_admin)
def approve_payment(request, payment_id):
    """Approve a pending payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status != 'pending':
        messages.warning(request, f'Payment {payment.reference} is already {payment.status}')
        return redirect('custom_admin:payment_detail', payment_id=payment_id)
    
    # Mark payment as completed
    payment.mark_as_completed()
    
    # Update related checkout status
    checkout = Checkout.objects.filter(
        user=payment.user,
        transaction_id=payment.reference
    ).first()
    
    if checkout:
        checkout.payment_status = 'completed'
        checkout.save()
        
        # Update related orders to processing
        Order.objects.filter(checkout=checkout, status='pending').update(
            status='processing',
            updated_at=timezone.now()
        )
    
    messages.success(request, f'Payment {payment.reference} has been approved and marked as completed!')
    return redirect('custom_admin:payment_detail', payment_id=payment_id)


@login_required
@user_passes_test(is_admin)
def reject_payment(request, payment_id):
    """Reject a pending payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status != 'pending':
        messages.warning(request, f'Payment {payment.reference} is already {payment.status}')
        return redirect('custom_admin:payment_detail', payment_id=payment_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', 'Payment rejected by admin')
        
        # Mark payment as failed
        payment.mark_as_failed(error_message=reason)
        
        # Update related checkout status
        checkout = Checkout.objects.filter(
            user=payment.user,
            transaction_id=payment.reference
        ).first()
        
        if checkout:
            checkout.payment_status = 'failed'
            checkout.save()
            
            # Update related orders to cancelled
            Order.objects.filter(checkout=checkout, status='pending').update(
                status='cancelled',
                updated_at=timezone.now()
            )
        
        messages.warning(request, f'Payment {payment.reference} has been rejected!')
        return redirect('custom_admin:payment_detail', payment_id=payment_id)
    
    return redirect('custom_admin:payment_detail', payment_id=payment_id)


@login_required
@user_passes_test(is_admin)
def mark_payment_processing(request, payment_id):
    """Mark payment as processing (under verification)"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status == 'pending':
        payment.status = 'processing'
        payment.save()
        messages.info(request, f'Payment {payment.reference} marked as processing')
    
    return redirect('custom_admin:payment_detail', payment_id=payment_id)



# --- Product Manual Management ---
from home.models import ProductManual
from home.forms import ProductManualForm
from django.http import HttpResponse, Http404


@login_required
@user_passes_test(is_admin)
def upload_product_manual(request, product_id):
    """Upload or replace a product manual."""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if manual already exists
    try:
        manual = product.manual
        is_replacement = True
    except ProductManual.DoesNotExist:
        manual = None
        is_replacement = False
    
    if request.method == 'POST':
        form = ProductManualForm(request.POST, request.FILES, instance=manual)
        if form.is_valid():
            # Delete old file if replacing
            if is_replacement and manual.file:
                old_file = manual.file
                try:
                    old_file.delete(save=False)
                except Exception as e:
                    messages.warning(request, f'Could not delete old file: {str(e)}')
            
            # Save new manual
            manual = form.save(commit=False)
            manual.product = product
            manual.uploaded_by = request.user
            manual.save()
            
            action = 'replaced' if is_replacement else 'uploaded'
            messages.success(request, f'Product manual {action} successfully for "{product.name}"!')
            return redirect('custom_admin:manage_products')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductManualForm(instance=manual)
    
    context = {
        'form': form,
        'product': product,
        'manual': manual,
        'is_replacement': is_replacement
    }
    return render(request, 'custom_admin/upload_product_manual.html', context)


@login_required
@user_passes_test(is_admin)
def delete_product_manual(request, product_id):
    """Delete a product manual."""
    product = get_object_or_404(Product, id=product_id)
    
    try:
        manual = product.manual
        manual_filename = manual.filename
        
        # Delete the file
        if manual.file:
            try:
                manual.file.delete(save=False)
            except Exception as e:
                messages.warning(request, f'Could not delete file: {str(e)}')
        
        # Delete the database record
        manual.delete()
        
        messages.success(request, f'Manual "{manual_filename}" deleted successfully for product "{product.name}"!')
    except ProductManual.DoesNotExist:
        messages.error(request, f'No manual found for product "{product.name}"')
    
    return redirect('custom_admin:manage_products')



# --- Platform Guide Management ---
from home.models import PlatformGuide, GuideAttachment
from home.forms import PlatformGuideForm, GuideAttachmentForm


@login_required
@user_passes_test(is_admin)
def guide_list(request):
    """List all platform guides with filtering."""
    guides = PlatformGuide.objects.all().order_by('display_order', '-created_at')
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        guides = guides.filter(category=category_filter)
    
    # Filter by published status
    status_filter = request.GET.get('status')
    if status_filter == 'published':
        guides = guides.filter(is_published=True)
    elif status_filter == 'draft':
        guides = guides.filter(is_published=False)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        guides = guides.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(guides, 20)
    page_number = request.GET.get('page')
    guides = paginator.get_page(page_number)
    
    context = {
        'guides': guides,
        'category_choices': PlatformGuide.CATEGORY_CHOICES,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'search_query': search_query
    }
    return render(request, 'custom_admin/guide_list.html', context)


@login_required
@user_passes_test(is_admin)
def manage_guide(request, guide_id=None):
    """Create new guide or edit existing guide."""
    if guide_id:
        guide = get_object_or_404(PlatformGuide, id=guide_id)
        is_edit = True
    else:
        guide = None
        is_edit = False
    
    if request.method == 'POST':
        form = PlatformGuideForm(request.POST, instance=guide)
        if form.is_valid():
            guide = form.save(commit=False)
            if not is_edit:
                guide.created_by = request.user
            guide.save()
            
            action = 'updated' if is_edit else 'created'
            messages.success(request, f'Guide "{guide.title}" {action} successfully!')
            return redirect('custom_admin:guide_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PlatformGuideForm(instance=guide)
    
    # Get attachments if editing
    attachments = guide.attachments.all() if guide else []
    
    context = {
        'form': form,
        'guide': guide,
        'is_edit': is_edit,
        'attachments': attachments
    }
    return render(request, 'custom_admin/manage_guide.html', context)


@login_required
@user_passes_test(is_admin)
def delete_guide(request, guide_id):
    """Delete a platform guide."""
    guide = get_object_or_404(PlatformGuide, id=guide_id)
    guide_title = guide.title
    
    # Delete all attachments (files will be deleted by signal handlers)
    guide.attachments.all().delete()
    
    # Delete the guide
    guide.delete()
    
    messages.success(request, f'Guide "{guide_title}" and all its attachments deleted successfully!')
    return redirect('custom_admin:guide_list')


@login_required
@user_passes_test(is_admin)
def upload_guide_attachment(request, guide_id):
    """Upload attachment for a guide."""
    guide = get_object_or_404(PlatformGuide, id=guide_id)
    
    if request.method == 'POST':
        form = GuideAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.guide = guide
            attachment.save()
            
            messages.success(request, f'Attachment uploaded successfully for guide "{guide.title}"!')
            return redirect('custom_admin:edit_guide', guide_id=guide_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = GuideAttachmentForm()
    
    context = {
        'form': form,
        'guide': guide
    }
    return render(request, 'custom_admin/upload_guide_attachment.html', context)


@login_required
@user_passes_test(is_admin)
def delete_guide_attachment(request, attachment_id):
    """Delete a guide attachment."""
    attachment = get_object_or_404(GuideAttachment, id=attachment_id)
    guide_id = attachment.guide.id
    
    # Delete the file
    if attachment.file:
        try:
            attachment.file.delete(save=False)
        except Exception as e:
            messages.warning(request, f'Could not delete file: {str(e)}')
    
    # Delete the database record
    attachment.delete()
    
    messages.success(request, 'Attachment deleted successfully!')
    return redirect('custom_admin:edit_guide', guide_id=guide_id)
