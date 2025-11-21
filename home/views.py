import os
import csv
import io
import uuid
import logging
from datetime import datetime
from io import StringIO

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from .receipt_generator import generate_receipt
from django.db import models
from django.utils import timezone

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from home.models import Product, Checkout, Category, Order, Sale, Profile
from cart.models import Cart
from .forms import (
    ProductForm,
    CheckoutForm,
    CategoryForm,
    ProfileForm,
    ContactForm,
)
from utils.mobile_money import MobileMoney


# --- Logging ---
logger = logging.getLogger(__name__)

# --- Demo MTN Mobile Money Credentials ---
MTN_API_USER = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
MTN_API_KEY = "5f4dcc3b5aa765d61d8327deb882cf99"
MTN_SUBSCRIPTION_KEY = "abc123def456ghi789jkl0mn"


# ===========================
# HOME & CATEGORY VIEWS
# ===========================

def home(request):
    """Homepage showing approved products and database categories."""
    print(f"DEBUG: Home view called at {request.path}")

    products = Product.objects.filter(status='active', approval_status='approved')
    cart_item_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0

    # Get categories from database
    db_categories = Category.objects.all()
    categories = []
    
    for category in db_categories:
        slug = category.name.lower().replace(" ", "-").replace("'", "")
        # Use icon from database or default
        icon = category.icon if category.icon else 'fas fa-shopping-bag'
        
        # Use image from database if available
        if category.image:
            category_image = category.image.url
        else:
            # Fallback to default icon display
            category_image = None
        
        categories.append({
            'name': category.name,
            'slug': slug,
            'icon': icon,
            'image': category_image,
            'db_id': category.id
        })

    return render(request, 'home/index.html', {
        'products': products,
        'categories': categories,
        'cart_item_count': cart_item_count,
    })


def about(request):
    return render(request, 'about.html')


def privacy_policy(request):
    return render(request, 'privacy_policy.html')


def terms_of_service(request):
    return render(request, 'terms_of_service.html')


def size_guide(request):
    return render(request, 'home/size_guide.html')


def delivery_info(request):
    return render(request, 'home/delivery_info.html')


def returns(request):
    return render(request, 'home/returns.html')


def faq(request):
    return render(request, 'home/faq.html')


# ===========================
# REPORTS VIEWS
# ===========================

@login_required
def reports_dashboard(request):
    """Main reports dashboard"""
    from home.reports import get_inventory_report
    from datetime import datetime
    
    # Check if user is staff or seller
    if not (request.user.is_staff or request.user.is_superuser or 
            Product.objects.filter(seller=request.user).exists()):
        messages.error(request, "You don't have permission to access reports.")
        return redirect('home:main_page')
    
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    inventory = get_inventory_report()
    
    context = {
        'current_year': current_year,
        'current_month': current_month,
        'inventory': inventory,
    }
    
    return render(request, 'home/reports_dashboard.html', context)


@login_required
def monthly_report(request):
    """Generate monthly report"""
    from home.reports import get_monthly_report, get_payment_report
    from datetime import datetime
    
    if not (request.user.is_staff or request.user.is_superuser or 
            Product.objects.filter(seller=request.user).exists()):
        messages.error(request, "You don't have permission to access reports.")
        return redirect('home:main_page')
    
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    seller = None if request.user.is_staff or request.user.is_superuser else request.user
    
    report_data = get_monthly_report(year, month, seller)
    payment_data = get_payment_report(year, month)
    
    context = {
        'report': report_data,
        'payment_data': payment_data,
        'year': year,
        'month': month,
        'is_admin': request.user.is_staff or request.user.is_superuser,
    }
    
    return render(request, 'home/monthly_report.html', context)


@login_req
    """Display all approved active products, optionally filter by category, search, and sort."""
    products = Product.objects.filter(status='active', approval_status='approved')
    categories = Category.objects.all()
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(
            models.Q(name__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(category__name__icontains=search_query)
        )
    
    # Sort functionality
    sort_by = request.GET.get('sort', '')
    if sort_by:
        products = products.order_by(sort_by)
    
    return render(request, 'home/products.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query,
    })


def category_products(request, category_slug):
    """Display products for a specific category using database categories."""
    # Get all categories from database
    db_categories = Category.objects.all()
    categories = []
    selected_category = None
    
    for category in db_categories:
        slug = category.slug if hasattr(category, 'slug') and category.slug else category.name.lower().replace(" ", "-").replace("'", "")
        icon = category.icon if category.icon else 'fas fa-shopping-bag'
        
        cat_data = {
            'name': category.name,
            'slug': slug,
            'icon': icon,
            'image': category.image.url if category.image else None,
            'db_id': category.id
        }
        categories.append(cat_data)
        
        if slug == category_slug:
            selected_category = cat_data
            selected_db_category = category

    if not selected_category:
        raise Http404("Category not found")

    # Get search query
    search_query = request.GET.get('search', '').strip()
    
    # Get products - search across all products if search query exists
    if search_query:
        products = Product.objects.filter(
            status='active',
            approval_status='approved'
        ).filter(
            models.Q(name__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(category__name__icontains=search_query)
        )
        search_performed = True
    else:
        # Get products for this category only
        products = Product.objects.filter(
            status='active',
            approval_status='approved',
            category=selected_db_category
        )
        search_performed = False

    return render(request, 'home/category_products.html', {
        'selected_category': selected_category,
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'search_performed': search_performed,
    })


# ===========================
# CATEGORY & PRODUCT MANAGEMENT
# ===========================

@login_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            category.save()
            messages.success(request, "Category created successfully!")
            return redirect('home:category_list')
    else:
        form = CategoryForm()
    return render(request, 'home/create_category.html', {'form': form})


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'home/category_list.html', {'categories': categories})


@login_required
def post_product(request):
    """Allow sellers to post new products."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, "Product posted successfully!")
            return redirect('home:products')
        messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm()
    return render(request, 'home/post_product.html', {'form': form})


@login_required
def update_product(request, id):
    product = get_object_or_404(Product, id=id, seller=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('home:product_detail', id=product.id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'home/update_product.html', {'form': form, 'product': product})


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('home:manage_products')
    return render(request, 'home/delete_product.html', {'product': product})


@login_required
def manage_products(request):
    products = Product.objects.filter(seller=request.user)
    # Debug: Print product info
    for product in products:
        print(f"Product: {product.name}")
        print(f"  - Has image: {bool(product.image)}")
        print(f"  - Static image: {product.static_image}")
        print(f"  - get_image_url(): {product.get_image_url()}")
    return render(request, 'home/manage_products.html', {'products': products})


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()
    return render(request, 'home/product_detail.html', {'product': product, 'categories': categories})


# ===========================
# CHECKOUT & ORDER VIEWS
# ===========================

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart:view_cart')

    # Calculate base price from cart items
    base_price = sum(item.get_total_price() for item in cart_items)
    
    # Default delivery fee (will be updated by JavaScript)
    default_delivery_fee = 30  # City center default
    total_price = base_price + default_delivery_fee

    return render(request, 'home/checkout.html', {
        'cart_items': cart_items, 
        'base_price': base_price,
        'total_price': total_price,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    })


def checkout_success(request):
    return render(request, 'home/checkout_success.html')


# ===========================
# SALES REPORTING & EXPORT
# ===========================

@login_required
def sales_report(request):
    sales_list = Sale.objects.filter(seller=request.user)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    product_id = request.GET.get('product')

    if start_date:
        sales_list = sales_list.filter(sale_date__gte=start_date)
    if end_date:
        sales_list = sales_list.filter(sale_date__lte=end_date)
    if product_id:
        sales_list = sales_list.filter(product__id=product_id)

    paginator = Paginator(sales_list, 10)
    sales = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'home/sales_report.html', {'sales': sales})


@login_required
def export_sales_csv(request):
    sales = Sale.objects.filter(seller=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Product', 'Buyer', 'Date', 'Quantity', 'Total'])
    for sale in sales:
        writer.writerow([
            sale.id,
            sale.product.name,
            sale.buyer.username,
            sale.sale_date.strftime('%Y-%m-%d'),
            sale.quantity,
            sale.total_amount,
        ])
    return response


@login_required
def export_sales_pdf(request):
    sales = Sale.objects.filter(seller=request.user)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, "Montclair Wardrobe Sales Report")
    p.drawString(100, 730, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y = 700
    for sale in sales:
        p.drawString(50, y, f"{sale.id} - {sale.product.name} - ZMW {sale.total_amount}")
        y -= 20
    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    return response


# ===========================
# PROFILE & ACCOUNT MANAGEMENT
# ===========================

@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'home/profile.html', {'profile': profile})


@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        profile.phone_number = request.POST.get('phone_number', profile.phone_number)
        profile.bio = request.POST.get('bio', profile.bio)
        profile.location = request.POST.get('location', profile.location)
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('home:profile')
    return render(request, 'home/edit_profile.html', {'profile': profile})


@login_required
def delete_account(request):
    if request.method == "POST":
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        if user:
            request.user.delete()
            messages.success(request, "Account deleted successfully.")
            logout(request)
            return redirect('home:main_page')
        messages.error(request, "Incorrect password.")
    return render(request, 'home/delete_account.html')


@login_required
def custom_password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully.")
            return redirect('password_change_done')
        messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'registration/password_change.html', {'form': form})


@login_required
def password_change_done_view(request):
    return render(request, 'registration/password_change_done.html')


# ===========================
# CONTACT & MISC
# ===========================

def contact_view(request):
    success = False
    form = ContactForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        subject = f"Montclair Wardrobe Contact: {data['subject']}"
        message = f"""
New contact form submission:

Name: {data['name']}
Email: {data['email']}
Subject: {data['subject']}

Message:
{data['message']}
        """
        try:
            send_mail(
                subject,
                message,
                'contact@montclairwardrobe.com',
                ['contact@montclairwardrobe.com'],
                fail_silently=False,
            )
            success = True
        except Exception as e:
            logger.error(f"Contact email failed: {e}")
            success = True  # Still show success in dev
    return render(request, 'home/contact.html', {'form': form, 'success': success})


def clock_view(request):
    return render(request, 'home/clock.html')


# ===========================
# ADMIN DASHBOARD
# ===========================

@login_required
def custom_admin_dashboard(request):
    return render(request, 'custom_admin/dashboard.html', {
        'total_users': User.objects.count(),
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
    })


@login_required
def manage_users(request):
    users = User.objects.all()
    return render(request, 'custom_admin/manage_users.html', {'users': users})


# ===========================
# AUTH HELPERS
# ===========================

def logout_view(request):
    """Handle logout for both GET and POST requests"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home:main_page')

def order_confirmation(request):
    """Display order confirmation page"""
    last_order = request.session.get('last_order')
    if not last_order:
        messages.error(request, "No recent order found.")
        return redirect('home:main_page')
    
    return render(request, 'home/checkout_success.html', {
        'order_number': last_order.get('order_number'),
        'total_amount': last_order.get('total_amount'),
        'payment_method': last_order.get('payment_method'),
        'delivery_area': last_order.get('delivery_area'),
        'checkout_id': last_order.get('checkout_id'),
        'now': timezone.now()
    })

@login_required
def user_checkouts(request):
    """Display user's order history"""
    orders = Order.objects.filter(user=request.user).select_related('product', 'checkout').order_by('-created_at')
    return render(request, 'home/user_checkouts.html', {
        'orders': orders
    })

@login_required
def checkout_process(request):
    """Process checkout form submission"""
    print(f"DEBUG: checkout_process called with method: {request.method}")
    
    if request.method == 'POST':
        try:
            print(f"DEBUG: POST data: {request.POST}")
            
            # Get cart items
            cart_items = Cart.objects.filter(user=request.user)
            print(f"DEBUG: Found {cart_items.count()} cart items for user {request.user}")
            
            if not cart_items.exists():
                messages.error(request, "Your cart is empty.")
                return redirect('cart:view_cart')
            
            # Get form data
            location_raw = request.POST.get('location')
            area_name = request.POST.get('area_name', '')
            street_address = request.POST.get('street_address', '')
            phone_number = request.POST.get('phone_number')
            gps_location = request.POST.get('gps_location')
            payment_method = request.POST.get('payment_method')
            total_price = request.POST.get('total_price')
            
            # Map location values to model choices
            location_mapping = {
                'city_center': 'inside',
                'residential': 'outside', 
                'compounds': 'outside',
                'suburbs': 'outside'
            }
            location = location_mapping.get(location_raw, 'outside')
            
            # Debug: Print form data
            print(f"DEBUG: Form data - location_raw: {location_raw}, mapped_location: {location}, phone: {phone_number}, payment: {payment_method}, total: {total_price}")
            
            # Validate required fields
            if not all([location_raw, phone_number, gps_location, payment_method]):
                missing_fields = []
                if not location_raw: missing_fields.append('location')
                if not phone_number: missing_fields.append('phone_number')
                if not gps_location: missing_fields.append('gps_location')
                if not payment_method: missing_fields.append('payment_method')
                
                print(f"DEBUG: Missing required fields: {missing_fields}")
                messages.error(request, f"Please fill in all required fields. Missing: {', '.join(missing_fields)}")
                return redirect('home:checkout')
            
            # Validate total_price
            if not total_price:
                print("DEBUG: Total price is missing")
                messages.error(request, "Invalid total price. Please try again.")
                return redirect('home:checkout')
            
            # Calculate totals using Decimal for proper arithmetic
            from decimal import Decimal
            cart_total = sum(item.get_total_price() for item in cart_items)
            print(f"DEBUG: Cart total: {cart_total}")
            
            try:
                total_price_decimal = Decimal(str(total_price))
                delivery_fee = total_price_decimal - cart_total
                print(f"DEBUG: Total price decimal: {total_price_decimal}, Delivery fee: {delivery_fee}")
            except Exception as e:
                print(f"DEBUG: Error converting total_price to decimal: {e}")
                messages.error(request, "Invalid total price format.")
                return redirect('home:checkout')
            
            # Import the correct Checkout model
            from home.models import Checkout
            from payment.models import Payment
            import time
            
            # Generate unique transaction reference
            transaction_ref = f"{payment_method.upper()}_{request.user.id}_{int(time.time())}"
            
            # Create checkout record
            print("DEBUG: Creating checkout record...")
            checkout = Checkout.objects.create(
                user=request.user,
                location=location,
                phone_number=phone_number,
                gps_location=gps_location,
                delivery_address=street_address,
                payment_method=payment_method,
                delivery_fee=delivery_fee,
                transaction_id=transaction_ref,
                payment_status='pending'
            )
            print(f"DEBUG: Checkout created with ID: {checkout.id}")
            
            # Create payment record for admin verification
            print("DEBUG: Creating payment record...")
            payment = Payment.objects.create(
                user=request.user,
                method=payment_method,
                amount=total_price_decimal,
                reference=transaction_ref,
                status='pending',
                phone_number=phone_number,
                location=location,
                gps_location=gps_location,
                hostel_name=area_name,
                room_number=street_address
            )
            print(f"DEBUG: Payment created with ID: {payment.id}, Reference: {payment.reference}")
            
            # Create orders for each cart item
            print("DEBUG: Creating orders...")
            for cart_item in cart_items:
                Order.objects.create(
                    user=request.user,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    total_price=cart_item.get_total_price(),
                    checkout=checkout
                )
                
                # Reduce product stock
                cart_item.product.reduce_stock(cart_item.quantity)
                
                # Create sale record
                Sale.objects.create(
                    product=cart_item.product,
                    seller=cart_item.product.seller,
                    buyer=request.user,
                    total_amount=cart_item.get_total_price(),
                    quantity=cart_item.quantity
                )
                print(f"DEBUG: Created order for product: {cart_item.product.name}")
            
            # Clear cart
            cart_items.delete()
            print("DEBUG: Cart cleared")
            
            # Store order details in session for confirmation page
            request.session['last_order'] = {
                'checkout_id': checkout.id,
                'order_number': f"MW{checkout.id:06d}",
                'total_amount': str(total_price),
                'payment_method': payment_method,
                'delivery_area': f"{area_name}, {location_raw}".strip(', ')
            }
            
            # Don't show message here - the confirmation page itself indicates success
            print("DEBUG: Redirecting to order confirmation")
            return redirect('home:order_confirmation')
            
        except Exception as e:
            import traceback
            print(f"DEBUG: Exception in checkout_process: {str(e)}")
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            messages.error(request, f"Error processing order: {str(e)}")
            return redirect('home:checkout')
    else:
        print("DEBUG: Non-POST request to checkout_process")
    
    return redirect('home:main_page')


@login_required
def checkout_detail(request, checkout_id):
    """Display detailed information about a specific checkout/order"""
    checkout = get_object_or_404(Checkout, id=checkout_id, user=request.user)
    orders = Order.objects.filter(checkout=checkout).select_related('product')
    
    return render(request, 'home/checkout_detail.html', {
        'order': checkout,  # Using 'order' to match template variable
        'checkout': checkout,
        'orders': orders
    })


# ===========================
# Review Views
# ===========================

@login_required
def submit_review(request, product_id):
    """
    Handle review submission with purchase verification.
    """
    from home.models import Product, Review
    from home.forms import ReviewForm
    
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user can review
    can_review, reason = Review.user_can_review(request.user, product)
    
    if not can_review:
        messages.error(request, reason)
        return redirect('home:product_detail', product_id=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        
        if form.is_valid():
            # Create review with verification
            review, created, error = Review.create_verified_review(
                user=request.user,
                product=product,
                rating=form.cleaned_data['rating'],
                title=form.cleaned_data['title'],
                comment=form.cleaned_data['comment']
            )
            
            if created:
                if review.is_verified_purchase:
                    messages.success(
                        request,
                        "Thank you for your verified review! It has been posted successfully."
                    )
                else:
                    messages.success(
                        request,
                        "Thank you for your review! It has been posted successfully."
                    )
                return redirect('home:product_detail', product_id=product_id)
            else:
                messages.error(request, error or "Unable to submit review.")
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ReviewForm()
    
    context = {
        'product': product,
        'form': form,
        'can_review': can_review,
        'reason': reason,
    }
    
    return render(request, 'home/submit_review.html', context)


@login_required
@require_POST
def delete_review(request, review_id):
    """
    Allow users to delete their own reviews.
    """
    from home.models import Review
    
    review = get_object_or_404(Review, id=review_id)
    
    # Check if user owns the review or is admin
    if review.user != request.user and not request.user.is_staff:
        messages.error(request, "You can only delete your own reviews.")
        return redirect('home:product_detail', product_id=review.product.id)
    
    product_id = review.product.id
    review.delete()
    
    messages.success(request, "Review deleted successfully.")
    return redirect('home:product_detail', product_id=product_id)


def product_reviews(request, product_id):
    """
    Display all reviews for a product.
    """
    from home.models import Product, Review
    from django.db.models import Avg, Count
    
    product = get_object_or_404(Product, id=product_id)
    
    # Get all reviews for the product
    reviews = Review.objects.filter(product=product).select_related('user')
    
    # Calculate statistics
    stats = reviews.aggregate(
        average_rating=Avg('rating'),
        total_reviews=Count('id'),
        verified_count=Count('id', filter=models.Q(is_verified_purchase=True))
    )
    
    # Rating distribution
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = reviews.filter(rating=i).count()
    
    # Pagination
    paginator = Paginator(reviews, 10)  # 10 reviews per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Check if current user can review
    can_review = False
    if request.user.is_authenticated:
        can_review, _ = Review.user_can_review(request.user, product)
    
    context = {
        'product': product,
        'reviews': page_obj,
        'stats': stats,
        'rating_distribution': rating_distribution,
        'can_review': can_review,
    }
    
    return render(request, 'home/product_reviews.html', context)



# Receipt Generation Views
@login_required
def download_receipt(request, checkout_id):
    """
    Generate and download PDF receipt for a checkout
    """
    # Get checkout and verify ownership
    checkout = get_object_or_404(Checkout, id=checkout_id, user=request.user)
    
    # Check if payment is completed
    if checkout.payment_status != 'completed':
        messages.warning(request, 'Receipt is only available for completed payments.')
        return redirect('home:user_checkouts')
    
    try:
        # Generate PDF receipt
        pdf_content = generate_receipt(checkout)
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_MW{checkout.id:06d}.pdf"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error generating receipt: {str(e)}')
        return redirect('home:checkout_detail', checkout_id=checkout_id)


@login_required
def view_receipt(request, checkout_id):
    """
    View PDF receipt inline in browser
    """
    # Get checkout and verify ownership
    checkout = get_object_or_404(Checkout, id=checkout_id, user=request.user)
    
    # Check if payment is completed
    if checkout.payment_status != 'completed':
        messages.warning(request, 'Receipt is only available for completed payments.')
        return redirect('home:user_checkouts')
    
    try:
        # Generate PDF receipt
        pdf_content = generate_receipt(checkout)
        
        # Create HTTP response with PDF for inline viewing
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="receipt_MW{checkout.id:06d}.pdf"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error generating receipt: {str(e)}')
        return redirect('home:checkout_detail', checkout_id=checkout_id)






# ===========================
# PRODUCT MANUAL VIEWS
# ===========================

def download_product_manual(request, product_id):
    """Serve product manual for download."""
    product = get_object_or_404(Product, id=product_id)
    
    try:
        manual = product.manual
        
        # Serve the file
        response = HttpResponse(manual.file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{manual.filename}"'
        return response
        
    except ProductManual.DoesNotExist:
        raise Http404("Manual not found for this product")
    except Exception as e:
        logger.error(f"Error downloading manual for product {product_id}: {str(e)}")
        messages.error(request, "Error downloading manual. Please try again later.")
        return redirect('home:product_detail', id=product_id)


# ===========================
# HELP CENTER VIEWS
# ===========================

from home.models import PlatformGuide, ProductManual


def help_center(request):
    """Display help center with guide categories and featured guides."""
    # Get featured guides
    featured_guides = PlatformGuide.objects.filter(
        is_published=True,
        featured=True
    ).order_by('display_order')[:3]
    
    # Get guides by category
    categories = {}
    for category_code, category_name in PlatformGuide.CATEGORY_CHOICES:
        guides = PlatformGuide.objects.filter(
            is_published=True,
            category=category_code
        ).order_by('display_order', '-created_at')[:5]
        
        if guides.exists():
            categories[category_code] = {
                'name': category_name,
                'guides': guides,
                'count': PlatformGuide.objects.filter(
                    is_published=True,
                    category=category_code
                ).count()
            }
    
    context = {
        'featured_guides': featured_guides,
        'categories': categories
    }
    return render(request, 'home/help_center.html', context)


def guide_detail(request, slug):
    """Display full guide content and increment view count."""
    guide = get_object_or_404(PlatformGuide, slug=slug, is_published=True)
    
    # Increment view count
    guide.increment_view_count()
    
    # Get related guides from same category
    related_guides = PlatformGuide.objects.filter(
        is_published=True,
        category=guide.category
    ).exclude(id=guide.id).order_by('display_order', '-created_at')[:3]
    
    context = {
        'guide': guide,
        'related_guides': related_guides
    }
    return render(request, 'home/guide_detail.html', context)


def guide_category(request, category):
    """Display guides filtered by category."""
    # Validate category
    valid_categories = dict(PlatformGuide.CATEGORY_CHOICES)
    if category not in valid_categories:
        raise Http404("Category not found")
    
    # Get guides for this category
    guides = PlatformGuide.objects.filter(
        is_published=True,
        category=category
    ).order_by('display_order', '-created_at')
    
    # Pagination
    paginator = Paginator(guides, 10)
    page_number = request.GET.get('page')
    guides = paginator.get_page(page_number)
    
    context = {
        'category_code': category,
        'category_name': valid_categories[category],
        'guides': guides
    }
    return render(request, 'home/guide_category.html', context)



# ===========================
# LIVE CHAT API VIEWS
# ===========================

from home.models import ChatSession, ChatMessage
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
@require_http_methods(["POST"])
def start_chat_session(request, product_id=None):
    """Initialize a chat session for customer."""
    try:
        data = json.loads(request.body)
        
        # Get or create session
        if request.user.is_authenticated:
            # Authenticated user
            session, created = ChatSession.objects.get_or_create(
                customer=request.user,
                status='active',
                defaults={
                    'product_id': product_id
                }
            )
        else:
            # Guest user
            guest_name = data.get('guest_name', '')
            guest_email = data.get('guest_email', '')
            
            if not guest_name or not guest_email:
                return JsonResponse({
                    'success': False,
                    'error': 'Name and email required for guests'
                }, status=400)
            
            session = ChatSession.objects.create(
                guest_name=guest_name,
                guest_email=guest_email,
                product_id=product_id,
                status='active'
            )
            created = True
        
        return JsonResponse({
            'success': True,
            'session_id': session.session_id,
            'created': created
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def send_message(request, session_id):
    """Send a message in a chat session."""
    try:
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            }, status=400)
        
        if len(message_text) > 1000:
            return JsonResponse({
                'success': False,
                'error': 'Message too long (max 1000 characters)'
            }, status=400)
        
        # Get session
        session = get_object_or_404(ChatSession, session_id=session_id)
        
        # Verify ownership
        if request.user.is_authenticated:
            # Authenticated user - check if they own the session
            if session.customer and session.customer != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Unauthorized'
                }, status=403)
            sender_name = request.user.get_full_name() or request.user.username
        else:
            # Guest user - session must not have a customer (must be guest session)
            if session.customer is not None:
                return JsonResponse({
                    'success': False,
                    'error': 'Unauthorized'
                }, status=403)
            sender_name = session.guest_name
        
        # Create message
        message = ChatMessage.objects.create(
            session=session,
            sender=request.user if request.user.is_authenticated else None,
            sender_name=sender_name,
            is_admin=False,
            message=message_text
        )
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'created_at': message.created_at.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_messages(request, session_id):
    """Poll for new messages (called every 3 seconds)."""
    try:
        session = get_object_or_404(ChatSession, session_id=session_id)
        
        # Get last message ID from query params
        last_message_id = request.GET.get('last_message_id', 0)
        
        # Get new messages
        messages = session.messages.filter(
            id__gt=last_message_id
        ).values(
            'id', 'sender_name', 'is_admin', 'message', 'created_at', 'is_read'
        )
        
        # Mark admin messages as read
        if not request.user.is_staff:
            session.messages.filter(
                id__gt=last_message_id,
                is_admin=True,
                is_read=False
            ).update(is_read=True)
        
        return JsonResponse({
            'success': True,
            'messages': list(messages),
            'unread_count': session.get_unread_count(for_admin=False)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def close_chat(request, session_id):
    """Close a chat session."""
    try:
        session = get_object_or_404(ChatSession, session_id=session_id)
        
        # Verify ownership
        if request.user.is_authenticated:
            if session.customer != request.user and not request.user.is_staff:
                return JsonResponse({
                    'success': False,
                    'error': 'Unauthorized'
                }, status=403)
        
        session.status = 'closed'
        session.save()
        
        return JsonResponse({
            'success': True
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ===========================
# ADMIN CHAT VIEWS
# ===========================

from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def admin_chat_dashboard(request):
    """Admin dashboard showing all chat sessions."""
    # Get filter parameters
    status_filter = request.GET.get('status', 'active')
    
    # Base queryset
    sessions = ChatSession.objects.select_related('customer', 'product', 'admin_assigned')
    
    # Apply filters
    if status_filter and status_filter != 'all':
        sessions = sessions.filter(status=status_filter)
    
    # Order by priority: unread first, then by last activity
    sessions = sessions.order_by('-last_message_at')
    
    # Get statistics
    stats = {
        'active': ChatSession.objects.filter(status='active').count(),
        'waiting': ChatSession.objects.filter(status='waiting').count(),
        'closed': ChatSession.objects.filter(status='closed').count(),
        'total_unread': sum(s.get_unread_count(for_admin=True) for s in ChatSession.objects.filter(status='active'))
    }
    
    context = {
        'sessions': sessions,
        'stats': stats,
        'current_filter': status_filter
    }
    return render(request, 'custom_admin/chat_dashboard.html', context)


@staff_member_required
def admin_chat_session(request, session_id):
    """Admin view for a specific chat session."""
    session = get_object_or_404(ChatSession, session_id=session_id)
    
    # Assign to current admin if not assigned
    if not session.admin_assigned:
        session.admin_assigned = request.user
        session.save()
    
    # Get all messages
    messages = session.messages.all().order_by('created_at')
    
    # Mark customer messages as read
    session.messages.filter(is_admin=False, is_read=False).update(is_read=True)
    
    context = {
        'session': session,
        'messages': messages
    }
    return render(request, 'custom_admin/chat_session.html', context)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def admin_send_message(request, session_id):
    """Admin sends a message to customer."""
    try:
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            }, status=400)
        
        if len(message_text) > 1000:
            return JsonResponse({
                'success': False,
                'error': 'Message too long (max 1000 characters)'
            }, status=400)
        
        # Get session
        session = get_object_or_404(ChatSession, session_id=session_id)
        
        # Create admin message
        message = ChatMessage.objects.create(
            session=session,
            sender=request.user,
            sender_name=request.user.get_full_name() or request.user.username,
            is_admin=True,
            message=message_text
        )
        
        # Update session status if it was waiting
        if session.status == 'waiting':
            session.status = 'active'
            session.save()
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'created_at': message.created_at.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
@require_http_methods(["GET"])
def admin_get_messages(request, session_id):
    """Admin polls for new messages from customer."""
    try:
        session = get_object_or_404(ChatSession, session_id=session_id)
        
        # Get last message ID from query params
        last_message_id = request.GET.get('last_message_id', 0)
        
        # Get new messages
        messages = session.messages.filter(
            id__gt=last_message_id
        ).values(
            'id', 'sender_name', 'is_admin', 'message', 'created_at', 'is_read'
        )
        
        # Mark customer messages as read
        session.messages.filter(
            id__gt=last_message_id,
            is_admin=False,
            is_read=False
        ).update(is_read=True)
        
        return JsonResponse({
            'success': True,
            'messages': list(messages),
            'unread_count': session.get_unread_count(for_admin=True)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def admin_close_chat(request, session_id):
    """Admin closes a chat session."""
    try:
        session = get_object_or_404(ChatSession, session_id=session_id)
        
        session.status = 'closed'
        session.save()
        
        return JsonResponse({
            'success': True
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def admin_assign_chat(request, session_id):
    """Assign chat session to an admin."""
    try:
        data = json.loads(request.body)
        admin_id = data.get('admin_id')
        
        session = get_object_or_404(ChatSession, session_id=session_id)
        
        if admin_id:
            admin_user = get_object_or_404(User, id=admin_id, is_staff=True)
            session.admin_assigned = admin_user
        else:
            session.admin_assigned = None
        
        session.save()
        
        return JsonResponse({
            'success': True,
            'assigned_to': session.admin_assigned.username if session.admin_assigned else None
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ===========================
# REPORTS VIEWS
# ===========================

@login_required
def reports_dashboard(request):
    """Main reports dashboard"""
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "You don't have permission to access reports.")
        return redirect('home:main_page')
    
    from home.reports import ReportGenerator
    from datetime import datetime, timedelta
    
    # Get current month data
    now = datetime.now()
    current_month = ReportGenerator.get_monthly_report(now.year, now.month)
    
    # Get last month data
    last_month = now.replace(day=1) - timedelta(days=1)
    previous_month = ReportGenerator.get_monthly_report(last_month.year, last_month.month)
    
    # Get current year data
    current_year = ReportGenerator.get_annual_report(now.year)
    
    # Get top products
    top_products = ReportGenerator.get_product_performance()[:10]
    
    context = {
        'current_month': current_month,
        'previous_month': previous_month,
        'current_year': current_year,
        'top_products': top_products,
    }
    
    return render(request, 'home/reports_dashboard.html', context)


@login_required
def generate_monthly_report(request):
    """Generate monthly report"""
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "You don't have permission to generate reports.")
        return redirect('home:main_page')
    
    from home.reports import ReportGenerator, generate_sales_csv
    
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    export_format = request.GET.get('format', 'html')
    
    report_data = ReportGenerator.get_monthly_report(year, month)
    
    if export_format == 'csv':
        filename = f'monthly_report_{year}_{month:02d}.csv'
        return generate_sales_csv(report_data['sales'], filename)
    
    elif export_format == 'pdf':
        from home.reports import ReportGenerator
        filename = f'monthly_report_{year}_{month:02d}.pdf'
        title = f'Monthly Sales Report - {datetime(year, month, 1).strftime("%B %Y")}'
        return ReportGenerator.export_to_pdf({'summary': report_data}, filename, title)
    
    context = {
        'report_data': report_data,
        'year': year,
        'month': month,
        'month_name': datetime(year, month, 1).strftime('%B'),
    }
    
    return render(request, 'home/monthly_report.html', context)


@login_required
def generate_annual_report(request):
    """Generate annual report"""
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "You don't have permission to generate reports.")
        return redirect('home:main_page')
    
    from home.reports import ReportGenerator, generate_sales_csv
    
    year = int(request.GET.get('year', datetime.now().year))
    export_format = request.GET.get('format', 'html')
    
    report_data = ReportGenerator.get_annual_report(year)
    
    if export_format == 'csv':
        filename = f'annual_report_{year}.csv'
        return generate_sales_csv(report_data['sales'], filename)
    
    elif export_format == 'pdf':
        from home.reports import ReportGenerator
        filename = f'annual_report_{year}.pdf'
        title = f'Annual Sales Report - {year}'
        return ReportGenerator.export_to_pdf({'summary': report_data}, filename, title)
    
    context = {
        'report_data': report_data,
        'year': year,
    }
    
    return render(request, 'home/annual_report.html', context)


@login_required
def product_performance_report(request):
    """Product performance report"""
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "You don't have permission to access reports.")
        return redirect('home:main_page')
    
    from home.reports import ReportGenerator, generate_product_performance_csv
    
    export_format = request.GET.get('format', 'html')
    
    products = ReportGenerator.get_product_performance()
    
    if export_format == 'csv':
        return generate_product_performance_csv(products, 'product_performance.csv')
    
    context = {
        'products': products,
    }
    
    return render(request, 'home/product_performance.html', context)
