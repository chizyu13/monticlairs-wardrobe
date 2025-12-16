from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from decimal import Decimal

from home.models import Order, Product
from staff_dashboard.models import StaffApproval, CustomerInquiry, StaffAuditLog
from staff_dashboard.services import StaffApprovalService, AuditLogService


@login_required
def staff_dashboard_home(request):
    """
    Display the staff dashboard home page with statistics and recent orders.
    """
    from django.core.cache import cache
    
    # Try to get cached statistics
    cache_key = f'dashboard_stats_{timezone.now().date()}'
    cached_stats = cache.get(cache_key)
    
    if cached_stats is None:
        # Get current date and time
        today = timezone.now().date()
        start_of_day = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        end_of_day = timezone.make_aware(datetime.combine(today, datetime.max.time()))
        
        # Get current month
        start_of_month = timezone.make_aware(
            datetime(today.year, today.month, 1, 0, 0, 0)
        )
        
        # Calculate statistics
        # Total orders count for current day
        total_orders_today = Order.objects.filter(
            created_at__gte=start_of_day,
            created_at__lte=end_of_day
        ).count()
        
        # Pending orders count
        pending_orders_count = Order.objects.filter(
            status='pending'
        ).count()
        
        # Low stock products count (stock <= 5)
        low_stock_count = Product.objects.filter(
            stock__lte=5,
            stock__gt=0,
            status='active'
        ).count()
        
        # Total revenue for current month
        revenue_data = Order.objects.filter(
            created_at__gte=start_of_month,
            status__in=['delivered', 'shipped', 'processing']
        ).aggregate(
            total=Sum('total_price')
        )
        total_revenue = revenue_data['total'] or Decimal('0.00')
        
        cached_stats = {
            'total_orders_today': total_orders_today,
            'pending_orders_count': pending_orders_count,
            'low_stock_count': low_stock_count,
            'total_revenue': total_revenue,
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, cached_stats, 300)
    
    # Get 10 most recent orders (not cached as it changes frequently)
    recent_orders = Order.objects.select_related(
        'user', 'product', 'checkout'
    ).order_by('-created_at')[:10]
    
    context = {
        **cached_stats,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'staff/dashboard_home.html', context)


@login_required
def staff_orders_list(request):
    """List all orders with filtering and pagination."""
    from django.core.paginator import Paginator
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    
    # Base queryset
    orders = Order.objects.select_related(
        'user', 'product', 'checkout'
    ).order_by('-created_at')
    
    # Apply status filter
    if status_filter and status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    # Apply search filter
    if search_query:
        orders = orders.filter(
            Q(user__username__icontains=search_query) |
            Q(product__name__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(orders, 25)  # 25 items per page
    page_obj = paginator.get_page(page_number)
    
    # Get status choices for filter dropdown
    status_choices = Order.StatusChoices.choices
    
    context = {
        'orders': page_obj,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': status_choices,
    }
    
    return render(request, 'staff/orders_list.html', context)


@login_required
def staff_order_detail(request, order_id):
    """Display detailed order information."""
    order = get_object_or_404(
        Order.objects.select_related('user', 'product', 'checkout'),
        id=order_id
    )
    
    context = {
        'order': order,
    }
    
    return render(request, 'staff/order_detail.html', context)


@login_required
def staff_order_update_status(request, order_id):
    """Update order status with validation and audit logging."""
    from django.contrib import messages
    from django.http import JsonResponse
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        # Validate status transition
        valid_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': [],
            'cancelled': [],
        }
        
        current_status = order.status
        
        if new_status not in valid_transitions.get(current_status, []):
            messages.error(
                request,
                f'Invalid status transition from {current_status} to {new_status}'
            )
            return redirect('staff_dashboard:order_detail', order_id=order_id)
        
        # Update order status
        old_status = order.status
        order.status = new_status
        order.save()
        
        # Log the action
        AuditLogService.log_action(
            staff_member=request.user,
            action='order_status_update',
            target_model='Order',
            target_id=order.id,
            changes={
                'old_status': old_status,
                'new_status': new_status,
                'order_id': order.id,
                'customer': order.user.username,
            }
        )
        
        messages.success(
            request,
            f'Order #{order.id} status updated to {new_status}'
        )
        
        return redirect('staff_dashboard:order_detail', order_id=order_id)
    
    return redirect('staff_dashboard:order_detail', order_id=order_id)


@login_required
def staff_products_list(request):
    """List all products with filtering and pagination."""
    from home.models import Category
    from django.core.paginator import Paginator
    from django.core.cache import cache
    
    # Get filter parameters
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    
    # Base queryset
    products = Product.objects.select_related(
        'seller', 'category'
    ).order_by('-created_at')
    
    # Apply category filter
    if category_filter and category_filter != 'all':
        products = products.filter(category_id=category_filter)
    
    # Apply status filter
    if status_filter and status_filter != 'all':
        products = products.filter(status=status_filter)
    
    # Apply search filter
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(seller__username__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(products, 25)  # 25 items per page
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter dropdown (cached)
    categories = cache.get('product_categories')
    if categories is None:
        categories = list(Category.objects.all())
        cache.set('product_categories', categories, 300)  # Cache for 5 minutes
    
    # Get status choices
    status_choices = Product.STATUS_CHOICES
    
    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': status_choices,
    }
    
    return render(request, 'staff/products_list.html', context)


@login_required
def staff_product_detail(request, product_id):
    """Display detailed product information."""
    from home.models import StockHistory
    
    product = get_object_or_404(
        Product.objects.select_related('seller', 'category'),
        id=product_id
    )
    
    # Get stock history
    stock_history = StockHistory.objects.filter(
        product=product
    ).select_related('changed_by').order_by('-created_at')[:20]
    
    context = {
        'product': product,
        'stock_history': stock_history,
    }
    
    return render(request, 'staff/product_detail.html', context)


@login_required
def staff_product_update(request, product_id):
    """Update product information and stock."""
    from django.contrib import messages
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # Get form data
        stock = request.POST.get('stock')
        status = request.POST.get('status')
        price = request.POST.get('price')
        
        changes = {}
        
        # Validate and update stock
        if stock is not None and stock != '':
            try:
                new_stock = int(stock)
                if new_stock < 0:
                    messages.error(request, 'Stock quantity cannot be negative')
                    return redirect('staff_dashboard:product_detail', product_id=product_id)
                
                if new_stock != product.stock:
                    old_stock = product.stock
                    product.stock = new_stock
                    changes['stock'] = {'old': old_stock, 'new': new_stock}
                    
                    # Record in stock history
                    from home.models import StockHistory
                    StockHistory.record_change(
                        product=product,
                        change_type='adjustment',
                        quantity_change=new_stock - old_stock,
                        reason='Staff adjustment',
                        changed_by=request.user
                    )
            except ValueError:
                messages.error(request, 'Invalid stock quantity')
                return redirect('staff_dashboard:product_detail', product_id=product_id)
        
        # Update status
        if status and status != product.status:
            changes['status'] = {'old': product.status, 'new': status}
            product.status = status
        
        # Update price
        if price:
            try:
                new_price = Decimal(price)
                if new_price != product.price:
                    changes['price'] = {'old': str(product.price), 'new': str(new_price)}
                    product.price = new_price
            except:
                messages.error(request, 'Invalid price')
                return redirect('staff_dashboard:product_detail', product_id=product_id)
        
        # Save product
        if changes:
            product.save()
            
            # Log the action
            AuditLogService.log_action(
                staff_member=request.user,
                action='product_update',
                target_model='Product',
                target_id=product.id,
                changes={
                    'product_id': product.id,
                    'product_name': product.name,
                    'changes': changes,
                }
            )
            
            messages.success(request, f'Product "{product.name}" updated successfully')
        else:
            messages.info(request, 'No changes were made')
        
        return redirect('staff_dashboard:product_detail', product_id=product_id)
    
    return redirect('staff_dashboard:product_detail', product_id=product_id)


@login_required
def staff_inquiries_list(request):
    """List customer inquiries with filtering."""
    from django.core.paginator import Paginator
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    
    # Base queryset
    inquiries = CustomerInquiry.objects.select_related(
        'customer', 'resolved_by'
    ).order_by('-created_at')
    
    # Apply status filter
    if status_filter and status_filter != 'all':
        inquiries = inquiries.filter(status=status_filter)
    
    # Apply search filter
    if search_query:
        inquiries = inquiries.filter(
            Q(subject__icontains=search_query) |
            Q(message__icontains=search_query) |
            Q(customer__username__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(inquiries, 25)  # 25 items per page
    page_obj = paginator.get_page(page_number)
    
    # Get status choices
    status_choices = CustomerInquiry.STATUS_CHOICES
    
    context = {
        'inquiries': page_obj,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': status_choices,
    }
    
    return render(request, 'staff/inquiries_list.html', context)


@login_required
def staff_inquiry_detail(request, inquiry_id):
    """Display inquiry details and responses."""
    from staff_dashboard.models import InquiryResponse
    
    inquiry = get_object_or_404(
        CustomerInquiry.objects.select_related('customer', 'resolved_by'),
        id=inquiry_id
    )
    
    # Get all responses
    responses = InquiryResponse.objects.filter(
        inquiry=inquiry
    ).select_related('staff_member').order_by('created_at')
    
    context = {
        'inquiry': inquiry,
        'responses': responses,
    }
    
    return render(request, 'staff/inquiry_detail.html', context)


@login_required
def staff_inquiry_resolve(request, inquiry_id):
    """Mark inquiry as resolved."""
    from django.contrib import messages
    
    inquiry = get_object_or_404(CustomerInquiry, id=inquiry_id)
    
    if request.method == 'POST':
        inquiry.status = 'resolved'
        inquiry.resolved_by = request.user
        inquiry.resolved_at = timezone.now()
        inquiry.save()
        
        # Log the action
        AuditLogService.log_action(
            staff_member=request.user,
            action='inquiry_resolved',
            target_model='CustomerInquiry',
            target_id=inquiry.id,
            changes={
                'inquiry_id': inquiry.id,
                'subject': inquiry.subject,
                'customer': inquiry.customer.username,
            }
        )
        
        messages.success(request, f'Inquiry "{inquiry.subject}" marked as resolved')
        return redirect('staff_dashboard:inquiry_detail', inquiry_id=inquiry_id)
    
    return redirect('staff_dashboard:inquiry_detail', inquiry_id=inquiry_id)


@login_required
def staff_inquiry_respond(request, inquiry_id):
    """Add a response to an inquiry."""
    from django.contrib import messages
    from staff_dashboard.models import InquiryResponse
    
    inquiry = get_object_or_404(CustomerInquiry, id=inquiry_id)
    
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        
        if not message_text:
            messages.error(request, 'Response message cannot be empty')
            return redirect('staff_dashboard:inquiry_detail', inquiry_id=inquiry_id)
        
        # Create response
        InquiryResponse.objects.create(
            inquiry=inquiry,
            staff_member=request.user,
            message=message_text
        )
        
        # Update inquiry status to in_progress if it was pending
        if inquiry.status == 'pending':
            inquiry.status = 'in_progress'
            inquiry.save()
        
        messages.success(request, 'Response added successfully')
        return redirect('staff_dashboard:inquiry_detail', inquiry_id=inquiry_id)
    
    return redirect('staff_dashboard:inquiry_detail', inquiry_id=inquiry_id)


# Admin views (superuser only)

def is_superuser(user):
    """Check if user is a superuser."""
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
def admin_staff_approval_list(request):
    """List all staff members with approval status."""
    from django.contrib.auth.models import User
    
    # Get all staff users (excluding superusers)
    staff_users = User.objects.filter(
        is_staff=True,
        is_superuser=False
    ).prefetch_related('staff_approval')
    
    # Get or create approval records
    staff_with_approval = []
    for user in staff_users:
        approval, created = StaffApproval.objects.get_or_create(user=user)
        staff_with_approval.append({
            'user': user,
            'approval': approval,
        })
    
    context = {
        'staff_list': staff_with_approval,
    }
    
    return render(request, 'staff/admin/approval_list.html', context)


@login_required
@user_passes_test(is_superuser)
def admin_staff_approve(request, user_id):
    """Approve a staff member."""
    from django.contrib import messages
    from django.contrib.auth.models import User
    
    user = get_object_or_404(User, id=user_id, is_staff=True)
    
    if request.method == 'POST':
        StaffApprovalService.approve_staff(user, request.user)
        messages.success(request, f'Staff member {user.username} has been approved')
    
    return redirect('staff_dashboard:admin_approval_list')


@login_required
@user_passes_test(is_superuser)
def admin_staff_revoke(request, user_id):
    """Revoke staff approval."""
    from django.contrib import messages
    from django.contrib.auth.models import User
    
    user = get_object_or_404(User, id=user_id, is_staff=True)
    
    if request.method == 'POST':
        StaffApprovalService.revoke_staff(user)
        messages.success(request, f'Staff approval for {user.username} has been revoked')
    
    return redirect('staff_dashboard:admin_approval_list')


@login_required
@user_passes_test(is_superuser)
def admin_audit_log(request):
    """View staff audit log with filtering."""
    # Get filter parameters
    staff_filter = request.GET.get('staff', '')
    action_filter = request.GET.get('action', '')
    
    # Get audit logs
    logs = AuditLogService.get_audit_log(limit=100)
    
    # Apply staff member filter
    if staff_filter and staff_filter != 'all':
        from django.contrib.auth.models import User
        try:
            staff_member = User.objects.get(id=staff_filter)
            logs = logs.filter(staff_member=staff_member)
        except User.DoesNotExist:
            pass
    
    # Apply action filter
    if action_filter and action_filter != 'all':
        logs = logs.filter(action=action_filter)
    
    # Get all staff members for filter
    from django.contrib.auth.models import User
    staff_members = User.objects.filter(is_staff=True).order_by('username')
    
    # Get action choices
    action_choices = StaffAuditLog.ACTION_CHOICES
    
    context = {
        'logs': logs,
        'staff_members': staff_members,
        'staff_filter': staff_filter,
        'action_filter': action_filter,
        'action_choices': action_choices,
    }
    
    return render(request, 'staff/admin/audit_log.html', context)
