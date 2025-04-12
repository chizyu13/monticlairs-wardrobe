from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, Checkout as CartCheckout
from home.models import Product

# ===========================
# View Cart
# ===========================
@login_required
def view_cart(request):
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

    if not product.is_in_stock():
        messages.error(request, f"{product.name} is not available (out of stock or not active).")
        return redirect('products')

    existing_cart_item = Cart.objects.filter(user=request.user, product=product).first()

    if existing_cart_item:
        if product.stock >= existing_cart_item.quantity + 1:
            existing_cart_item.quantity += 1
            existing_cart_item.save()
            messages.success(request, f"Updated quantity of {product.name} in your cart.")
        else:
            messages.warning(request, f"Cannot add more {product.name}. Only {product.stock} left in stock.")
    else:
        Cart.objects.create(user=request.user, product=product, quantity=1)
        messages.success(request, f"{product.name} has been added to your cart.")

    return redirect('cart:view_cart')

# ===========================
# Update Cart
# ===========================
@login_required
def update_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, f"Quantity updated to {quantity}.")
            else:
                cart_item.delete()
                messages.info(request, "Item removed from cart.")
        except ValueError:
            messages.error(request, "Invalid quantity.")

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
