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


def products(request):
    """Display all approved active products, optionally filter by category."""
    products = Product.objects.filter(status='active', approval_status='approved')
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    return render(request, 'home/products.html', {'products': products, 'categories': categories})


def category_products(request, category_slug):
    """Display products for a specific category."""
    static_images_path = os.path.join(settings.BASE_DIR, 'static', 'images')
    categories = []
    selected_category = None

    category_icons = {
        'jewelry': 'fas fa-gem',
        'kids': 'fas fa-child',
        'ladies-wear': 'fas fa-female',
        'mens-wear': 'fas fa-male',
        'msimbi-babies': 'fas fa-baby',
        'shoes': 'fas fa-shoe-prints',
        'sports-wear': 'fas fa-running',
        'watches': 'fas fa-clock',
    }

    if os.path.exists(static_images_path):
        for item in os.listdir(static_images_path):
            item_path = os.path.join(static_images_path, item)
            if os.path.isdir(item_path):
                folder_slug = item.lower().replace(' ', '-').replace("'", "")
                icon = category_icons.get(folder_slug, 'fas fa-shopping-bag')
                
                # Look for category image (same logic as home view)
                category_image = None
                image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
                
                for ext in image_extensions:
                    for name in ['category', 'cover', 'main', 'hero']:
                        potential_image = os.path.join(item_path, f"{name}{ext}")
                        if os.path.exists(potential_image):
                            category_image = f"images/{item}/{name}{ext}"
                            break
                    if category_image:
                        break
                
                if not category_image:
                    try:
                        files = os.listdir(item_path)
                        for file in files:
                            if any(file.lower().endswith(ext) for ext in image_extensions):
                                category_image = f"images/{item}/{file}"
                                break
                    except (OSError, PermissionError):
                        pass
                
                if not category_image:
                    default_images = {
                        'jewerly': 'images/defaults/jewelry-default.jpg',
                        'jewelry': 'images/defaults/jewelry-default.jpg',
                        'kids': 'images/defaults/kids-default.jpg',
                        'ladies-wear': 'images/defaults/ladies-default.jpg',
                        'mens-wear': 'images/defaults/mens-default.jpg',
                        'men-s-wear': 'images/defaults/mens-default.jpg',
                        'msimbi-babies': 'images/defaults/babies-default.jpg',
                        'shoes': 'images/defaults/shoes-default.jpg',
                        'sports-wear': 'images/defaults/sports-default.jpg',
                        'watches': 'images/defaults/watches-default.jpg'
                    }
                    category_image = default_images.get(folder_slug, 'images/defaults/category-default.jpg')
                
                cat_data = {
                    'name': item, 
                    'slug': folder_slug, 
                    'icon': icon,
                    'image': category_image,
                    'folder_name': item
                }
                categories.append(cat_data)
                if folder_slug == category_slug:
                    selected_category = cat_data

    if not selected_category:
        raise Http404("Category not found")

    products = Product.objects.filter(status='active', approval_status='approved')
    
    # Create a mapping from folder names to database category names
    folder_to_db_category = {
        'Watches': 'Watches',
        'Jewerly': 'Jewerly',  # Keep the typo as it exists in DB
        'Kids': 'Kids',
        'Ladies-Wear': 'Ladies Wear',
        'Mens-Wear': 'Men\'s Wear',
        'Baby-Wear': 'Msimbi (Babies)',
        'Shoes': 'Shoes',
        'Sports-Wear': 'Sports Wear',
    }
    
    # Try to find the category using the mapping
    folder_name = selected_category['folder_name']
    db_category_name = folder_to_db_category.get(folder_name, selected_category['name'])
    
    try:
        db_category = Category.objects.get(name=db_category_name)
        products = products.filter(category=db_category)
        print(f"Found category: {db_category.name}, Products count: {products.count()}")
    except Category.DoesNotExist:
        print(f"Category not found: {db_category_name}")
        # Try alternative names
        alternative_names = [
            selected_category['name'],
            folder_name,
            folder_name.replace('-', ' '),
            folder_name.replace('-', '\'s ') if 'mens' in folder_name.lower() else folder_name
        ]
        
        for alt_name in alternative_names:
            try:
                db_category = Category.objects.get(name__iexact=alt_name)
                products = products.filter(category=db_category)
                print(f"Found alternative category: {db_category.name}")
                break
            except Category.DoesNotExist:
                continue

    return render(request, 'home/category_products.html', {
        'selected_category': selected_category,
        'products': products,
        'categories': categories,
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
        'total_price': total_price
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



