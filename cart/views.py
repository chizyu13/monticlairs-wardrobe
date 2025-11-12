from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, Checkout as CartCheckout
from home.models import Product, StockReservation

# ===========================
# Helper: Validate Cart Stock
# ===========================
def validate_cart_stock(user):
    """
    Validate that all items in the cart have sufficient stock.
    Returns a tuple: (is_valid, error_messages, items_removed)
    """
    cart_items = Cart.objects.filter(user=user).select_related('product')
    error_messages = []
    items_removed = []
    is_valid = True
    
    for item in cart_items:
        product = item.product
        
        # Check if product is still available
        if not product.is_in_stock():
            error_messages.append(
                f"{product.name} is no longer available and has been removed from your cart."
            )
            items_removed.append(product.name)
            item.delete()
            is_valid = False
            continue
        
        # Check if sufficient stock is available
        if item.quantity > product.stock:
            if product.stock > 0:
                # Adjust quantity to available stock
                old_quantity = item.quantity
                item.quantity = product.stock
                item.save()
                error_messages.append(
                    f"{product.name} quantity adjusted from {old_quantity} to {product.stock} "
                    f"(maximum available stock)."
                )
                is_valid = False
            else:
                # Remove item if no stock available
                error_messages.append(
                    f"{product.name} is out of stock and has been removed from your cart."
                )
                items_removed.append(product.name)
                item.delete()
                is_valid = False
    
    return is_valid, error_messages, items_removed

# ===========================
# View Cart
# ===========================
@login_required
def view_cart(request):
    # Validate cart stock before displaying
    is_valid, error_messages, items_removed = validate_cart_stock(request.user)
    
    # Display any stock-related messages
    for message in error_messages:
        messages.warning(request, message)
    
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    total_price = sum(item.get_total_price() for item in cart_items)
    cart_item_count = cart_items.count()

    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_item_count': cart_item_count,
    })

# ===========================
# Add to Cart
# ===========================
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Prevent admins from purchasing
    if request.user.is_superuser or request.user.is_staff:
        messages.error(request, "Admin accounts cannot purchase products.")
        return redirect('home:products')
    
    # Prevent sellers from buying their own products
    if product.seller == request.user:
        messages.error(request, "You cannot purchase your own product.")
        return redirect('home:products')

    # Check if product is available for purchase
    if not product.is_in_stock():
        messages.error(request, f"{product.name} is not available (out of stock or not active).")
        return redirect('home:products')
    
    # Check stock availability
    if product.stock <= 0:
        messages.error(request, f"{product.name} is currently out of stock.")
        return redirect('home:products')

    existing_cart_item = Cart.objects.filter(user=request.user, product=product).first()

    if existing_cart_item:
        # Check if adding one more would exceed available stock
        new_quantity = existing_cart_item.quantity + 1
        
        if new_quantity > product.stock:
            messages.warning(
                request, 
                f"Cannot add more {product.name}. Only {product.stock} available in stock "
                f"(you already have {existing_cart_item.quantity} in your cart)."
            )
            return redirect('cart:view_cart')
        
        # Update quantity
        existing_cart_item.quantity = new_quantity
        existing_cart_item.save()
        messages.success(
            request, 
            f"Updated quantity of {product.name} to {new_quantity} in your cart."
        )
    else:
        # Create new cart item
        Cart.objects.create(user=request.user, product=product, quantity=1)

    return redirect('cart:view_cart')

# ===========================
# Update Cart
# ===========================
@login_required
def update_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    product = cart_item.product

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            
            if quantity <= 0:
                # Remove item if quantity is 0 or negative
                product_name = product.name
                cart_item.delete()
                messages.info(request, f"{product_name} removed from cart.")
                return redirect('cart:view_cart')
            
            # Validate stock availability
            if quantity > product.stock:
                messages.error(
                    request,
                    f"Cannot update quantity. Only {product.stock} units of {product.name} available in stock. "
                    f"Your cart quantity remains at {cart_item.quantity}."
                )
                return redirect('cart:view_cart')
            
            # Check if product is still available
            if not product.is_in_stock():
                messages.error(
                    request,
                    f"{product.name} is no longer available. Removing from cart."
                )
                cart_item.delete()
                return redirect('cart:view_cart')
            
            # Update quantity
            old_quantity = cart_item.quantity
            cart_item.quantity = quantity
            cart_item.save()
            
            messages.success(
                request, 
                f"Updated {product.name} quantity from {old_quantity} to {quantity}."
            )
            
        except ValueError:
            messages.error(request, "Invalid quantity. Please enter a valid number.")
        except Exception as e:
            messages.error(request, f"Error updating cart: {str(e)}")

    return redirect('cart:view_cart')

# ===========================
# Remove from Cart
# ===========================
@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart:view_cart')

# ===========================
# Empty Cart (for guest + logged in)
# ===========================
def empty_cart(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            Cart.objects.filter(user=request.user).delete()
            messages.success(request, "Your cart has been emptied.")
        else:
            request.session['cart'] = {}
            messages.success(request, "Your cart session has been emptied.")
        return render(request, 'cart/empty_cart.html')
    return redirect('cart:view_cart')

# ===========================
# Clear Cart (for logged-in only)
# ===========================
@login_required
def clear_cart(request):
    Cart.objects.filter(user=request.user).delete()
    messages.success(request, "Your cart has been cleared.")
    return redirect('cart:view_cart')

# ===========================
# Reserve Stock for Checkout
# ===========================
@login_required
def reserve_stock_for_checkout(request):
    """
    Reserve stock for all items in the cart before proceeding to checkout.
    This prevents stock from being sold to others during the checkout process.
    """
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart:view_cart')
    
    # Validate and create reservations
    reservations_created = []
    errors = []
    
    for item in cart_items:
        product = item.product
        
        # Check if product is still available
        if not product.is_in_stock():
            errors.append(f"{product.name} is no longer available.")
            continue
        
        # Check available stock (accounting for existing reservations)
        available = StockReservation.get_available_stock(product)
        
        if item.quantity > available:
            errors.append(
                f"Only {available} units of {product.name} available. "
                f"Please update your cart."
            )
            continue
        
        # Create or update reservation
        reservation, created = StockReservation.create_reservation(
            user=request.user,
            product=product,
            quantity=item.quantity,
            expiry_minutes=15  # 15 minutes to complete checkout
        )
        reservations_created.append(reservation)
    
    if errors:
        for error in errors:
            messages.error(request, error)
        return redirect('cart:view_cart')
    
    if reservations_created:
        messages.success(
            request,
            f"Stock reserved for {len(reservations_created)} item(s). "
            f"Please complete checkout within 15 minutes."
        )
        # Redirect to actual checkout page
        return redirect('home:checkout')
    else:
        messages.error(request, "Unable to reserve stock. Please try again.")
        return redirect('cart:view_cart')

# ===========================
# Example Checkout View (placeholder)
# ===========================
@login_required
def checkout_view(request):
    # This is a placeholder logic, add your real checkout processing here
    success = True  # Simulate success/failure
    if success:
        messages.success(request, "Checkout completed successfully!")
    else:
        messages.error(request, "Something went wrong during checkout.")
    return redirect('cart:view_cart')

# ===========================
# Example: Using Multiple Checkout Models
# ===========================
@login_required
def some_view(request):
    cart_checkouts = request.user.cart_checkouts.all()
    try:
        home_checkouts = request.user.home_checkouts.all()
    except:
        home_checkouts = []

    context = {
        "cart_checkouts": cart_checkouts,
        "home_checkouts": home_checkouts,
    }
    return render(request, "cart/cart.html", context)
