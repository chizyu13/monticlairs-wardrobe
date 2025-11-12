"""
Accounts App Models

This app previously contained duplicate models (Profile, Cart, Product) that were
already defined in other apps. These duplicates have been removed to prevent conflicts.

Active Models:
- Profile: Use home.Profile
- Cart: Use cart.Cart  
- Product: Use home.Product

If you need to reference these models in this app, import them from their primary locations:
    from home.models import Profile, Product
    from cart.models import Cart
"""

# This file intentionally left minimal to avoid model duplication
# All models are managed by their respective apps (home, cart, payment)
