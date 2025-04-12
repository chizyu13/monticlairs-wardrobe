from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
import csv
from django.contrib.auth.models import User
from io import StringIO
import uuid
from home.models import Product, Checkout, Category, Order, Sale, Profile
from cart.models import Cart
from .forms import ProductForm, CheckoutForm, CategoryForm, ProfileForm
from utils.mobile_money import MobileMoney
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Sample credentials (for demo only)
MTN_API_USER = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
MTN_API_KEY = "5f4dcc3b5aa765d61d8327deb882cf99"
MTN_SUBSCRIPTION_KEY = "abc123def456ghi789jkl0mn"

def home(request):
    products = Product.objects.filter(status='active')
    cart_item_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'home/index.html', {
        'products': products,
        'cart_item_count': cart_item_count
    })

def about(request):
    return render(request, 'about.html')

def products(request):
    products = Product.objects.filter(status='active')
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    return render(request, 'home/products.html', {
        'products': products,
        'categories': categories
    })

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')

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
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, "Product posted successfully!")
            return redirect('home:products')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm()
    return render(request, 'home/post_product.html', {'form': form})

from .mobile_money import MobileMoney  # Assuming this is your payment integration
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CheckoutForm

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart:view_cart')

    base_price = sum(item.get_total_price() for item in cart_items)

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            checkout = form.save(commit=False)
            checkout.user = request.user
            checkout.delivery_fee = 20 if checkout.location == 'inside' else 50
            checkout.save()

            for item in cart_items:
                product = item.product
                quantity = item.quantity
                try:
                    product.reduce_stock(quantity)
                    order = Order.objects.create(
                        user=request.user,
                        product=product,
                        quantity=quantity,
                        total_price=item.get_total_price(),
                        checkout=checkout
                    )
                    Sale.objects.create(
                        product=product,
                        seller=product.seller,
                        buyer=request.user,
                        total_amount=item.get_total_price(),
                        quantity=quantity
                    )
                except ValueError as e:
                    messages.error(request, str(e))
                    return redirect('cart:view_cart')

                item.delete()

            messages.success(request, "Checkout successful! Your order has been placed.")
            return redirect('checkout_success')  # Replace with your actual success page/view
        else:
            messages.error(request, "There was an error with your checkout form.")
    else:
        form = CheckoutForm()

    return render(request, 'home/checkout.html', {
        'cart_items': cart_items,
        'form': form,
        'base_price': base_price,
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()
    return render(request, 'home/product_detail.html', {
        'product': product,
        'categories': categories,
    })

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
def custom_admin_dashboard(request):
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
    }
    return render(request, 'custom_admin/dashboard.html', context)

@login_required
def manage_users(request):
    users = User.objects.all()
    return render(request, 'custom_admin/manage_users.html', {'users': users})

@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'home/profile_view.html', {'profile': profile})

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

        messages.success(request, "Your profile has been updated successfully.")
        return redirect('home:profile_view')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'home/edit_profile.html', {'form': form, 'user': request.user})

@login_required
def delete_account(request):
    if request.method == "POST":
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        if user is not None:
            request.user.delete()
            messages.success(request, "Your account has been successfully deleted.")
            logout(request)
            return redirect('home')
        else:
            messages.error(request, "Incorrect password. Please try again.")
    return render(request, 'home/delete_account.html')

@login_required
def user_checkouts(request):
    checkouts = request.user.checkouts.all()  # Assumes related_name='checkouts' in Checkout model
    return render(request, 'home/user_checkout.html', {'checkouts': checkouts})

@login_required
def sales_report(request):
    sales_list = Sale.objects.filter(seller=request.user)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    product_id = request.GET.get('product')

    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            sales_list = sales_list.filter(sale_date__gte=start_datetime)
        except ValueError:
            logger.warning(f"Invalid start_date format: {start_date}")
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            sales_list = sales_list.filter(sale_date__lte=end_datetime)
        except ValueError:
            logger.warning(f"Invalid end_date format: {end_date}")
    if product_id:
        try:
            sales_list = sales_list.filter(product__id=product_id)
        except ValueError:
            logger.warning(f"Invalid product_id: {product_id}")

    paginator = Paginator(sales_list, 10)
    page_number = request.GET.get('page', 1)
    
    try:
        page_number = int(page_number)
        if page_number < 1:
            page_number = 1
    except ValueError:
        page_number = 1
    
    sales = paginator.get_page(page_number)
    return render(request, 'home/sales_report.html', {
        'sales': sales,
        'start_date': start_date,
        'end_date': end_date,
        'product_id': product_id
    })
@login_required
def generate_receipt(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id, seller=request.user)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{sale.id}.pdf"'

    c = canvas.Canvas(response, pagesize=letter)
    c.drawString(100, 750, f"Receipt for Sale #{sale.id}")
    c.drawString(100, 730, f"Product: {sale.product.name}")
    c.drawString(100, 710, f"Seller: {sale.seller.username}")
    c.drawString(100, 690, f"Buyer: {sale.buyer.username}")
    c.drawString(100, 670, f"Sale Date: {sale.sale_date.strftime('%Y-%m-%d %H:%M')}")
    c.drawString(100, 650, f"Total Amount: ZMW {sale.total_amount:.2f}")
    c.showPage()
    c.save()
    return response

@login_required
def export_sales(request):
    sales = Sale.objects.filter(seller=request.user)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        sales = sales.filter(sale_date__gte=start_date)
    if end_date:
        sales = sales.filter(sale_date__lte=end_date)
    
    export_format = request.GET.get('format', 'csv')
    
    if export_format == 'csv':
        return export_sales_csv(sales)
    elif export_format == 'pdf':
        return export_sales_pdf(request)  # Call the new function directly with request
    else:
        return HttpResponse("Invalid export format", status=400)

def export_sales_csv(sales):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Product', 'Buyer', 'Sale Date', 'Quantity', 'Total Amount'])
    for sale in sales:
        writer.writerow([
            sale.id,
            sale.product.name,
            sale.buyer.username,
            sale.sale_date.strftime('%Y-%m-%d'),
            sale.quantity,
            sale.total_amount
        ])
    return response
@login_required
def export_sales_pdf(request):
    """
    Export sales report as a PDF using reportlab, excluding unit_price.
    """
    try:
        # Get filter parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        product_id = request.GET.get('product')
        logger.debug(f"Filters: start_date={start_date}, end_date={end_date}, product_id={product_id}")

        # Build queryset
        sales = Sale.objects.filter(seller=request.user)
        logger.debug(f"Initial sales count: {sales.count()}")
        if start_date:
            try:
                sales = sales.filter(sale_date__gte=start_date)
                logger.debug(f"After start_date filter: {sales.count()}")
            except ValueError as e:
                logger.warning(f"Invalid start_date format: {start_date}, Error: {e}")
                start_date = None
        if end_date:
            try:
                sales = sales.filter(sale_date__lte=end_date)
                logger.debug(f"After end_date filter: {sales.count()}")
            except ValueError as e:
                logger.warning(f"Invalid end_date format: {end_date}, Error: {e}")
                end_date = None
        if product_id:
            try:
                sales = sales.filter(product__id=product_id)
                logger.debug(f"After product_id filter: {sales.count()}")
            except ValueError as e:
                logger.warning(f"Invalid product_id: {product_id}, Error: {e}")
                product_id = None

        # Calculate summary stats
        total_sales_count = sales.count()
        total_revenue = sum(float(sale.total_amount or 0) for sale in sales) if sales else 0
        average_sale = total_revenue / total_sales_count if total_sales_count > 0 else 0
        monthly_sales = Sale.objects.filter(
            seller=request.user,
            sale_date__month=datetime.now().month,
            sale_date__year=datetime.now().year
        )
        monthly_revenue = sum(float(sale.total_amount or 0) for sale in monthly_sales) if monthly_sales.exists() else 0
        logger.debug(f"Stats: total_sales={total_sales_count}, total_revenue={total_revenue}, average_sale={average_sale}, monthly_revenue={monthly_revenue}")

        # Create PDF
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica", 12)

        # Header
        p.drawString(50, 750, "EHC Marketplace Sales Report")
        p.drawString(50, 730, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        y_offset = 710
        if start_date or end_date:
            date_range = f"Date Range: {start_date or 'Start'} to {end_date or 'End'}"
            p.drawString(50, y_offset, date_range[:60])
            y_offset -= 20
        if product_id:
            try:
                product = get_object_or_404(Product, id=product_id)
                p.drawString(50, y_offset, f"Product: {product.name[:50]}")
                y_offset -= 20
            except Exception as e:
                logger.error(f"Error fetching product {product_id}: {e}")

        # Table headers (no unit_price)
        y = 650
        headers = ["#", "Product", "Buyer", "Date", "Qty", "Total", "Status"]
        x_positions = [50, 80, 200, 300, 380, 420, 500]  # Adjusted positions
        for i, header in enumerate(headers):
            p.drawString(x_positions[i], y, header)
        p.line(50, y-5, 550, y-5)

        # Table data (no unit_price)
        y -= 20
        for idx, sale in enumerate(sales, 1):
            if y < 50:
                p.showPage()
                p.setFont("Helvetica", 12)
                y = 750
                for i, header in enumerate(headers):
                    p.drawString(x_positions[i], y, header)
                p.line(50, y-5, 550, y-5)
                y -= 20
            try:
                p.drawString(x_positions[0], y, str(idx))
                p.drawString(x_positions[1], y, (sale.product.name[:20] if sale.product and hasattr(sale.product, 'name') else "N/A"))
                p.drawString(x_positions[2], y, (sale.buyer.username[:15] if sale.buyer and hasattr(sale.buyer, 'username') else "Unknown"))
                p.drawString(x_positions[3], y, (sale.sale_date.strftime('%Y-%m-%d') if sale.sale_date else "N/A"))
                p.drawString(x_positions[4], y, str(sale.quantity) if sale.quantity is not None else "0")
                p.drawString(x_positions[5], y, f"ZMW {float(sale.total_amount):.2f}" if sale.total_amount is not None else "ZMW 0.00")
                p.drawString(x_positions[6], y, sale.status.title() if sale.status else "Unknown")
            except Exception as e:
                logger.error(f"Error processing sale {sale.id}: {e}")
            y -= 20

        # Summary
        y -= 20
        p.drawString(50, y, f"Total Revenue: ZMW {total_revenue:.2f}")
        y -= 20
        p.drawString(50, y, f"Total Sales: {total_sales_count}")
        y -= 20
        p.drawString(50, y, f"Average Sale: ZMW {average_sale:.2f}")
        y -= 20
        p.drawString(50, y, f"Monthly Revenue ({datetime.now().strftime('%B %Y')}): ZMW {monthly_revenue:.2f}")

        p.showPage()
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
        return response

    except Exception as e:
        logger.error(f"Unexpected error in export_sales_pdf: {e}")
        return HttpResponse("An unexpected error occurred while generating the PDF", status=500)
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('home:profile')
    return render(request, 'home/delete-product.html', {'product': product})

@login_required
def toggle_product_status(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if product.status == Product.STATUS_CHOICES.ACTIVE:
        product.status = Product.STATUS_CHOICES.SOLD
    elif product.status == Product.STATUS_CHOICES.SOLD:
        product.status = Product.STATUS_CHOICES.ACTIVE
    product.save()
    messages.success(request, "Product status updated!")
    return redirect('home:sales_report')

def sale_detail(request, id):
    sale = get_object_or_404(Sale, id=id)
    return render(request, 'home/sale_detail.html', {'sale': sale})

def checkout_detail(request, pk):
    checkout = get_object_or_404(Checkout, pk=pk)
    return render(request, 'home/checkout_detail.html', {'checkout': checkout})

def checkout_process(request):
    checkouts = Checkout.objects.all()
    return render(request, 'home/checkout_process.html', {'checkouts': checkouts})

@login_required
def manage_products(request):
    user_products = Product.objects.filter(seller=request.user)
    cart_items = Cart.objects.filter(user=request.user)
    return render(request, 'home/manage_products.html', {
        'products': user_products,
        'cart_item_count': cart_items.count(),
    })

@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

@login_required(login_url='login')
def products_view(request):
    return render(request, 'products.html')

from django.shortcuts import render

def checkout_success(request):
    return render(request, 'home/checkout_success.html')

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages

# Password Change View
@login_required
def custom_password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password_change_done')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'registration/password_change.html', {'form': form})

# Password Change Done View
@login_required
def password_change_done_view(request):
    return render(request, 'registration/password_change_done.html')
