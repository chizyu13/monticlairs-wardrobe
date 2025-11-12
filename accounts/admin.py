"""
Accounts Admin Configuration

Note: The Profile model has been moved to home.models.Profile to avoid duplication.
If you need to manage profiles in the admin, they are registered in home/admin.py

All models are now managed in their respective apps:
- Profile: home/admin.py
- Product: home/admin.py
- Cart: cart/admin.py (if needed)
"""

from django.contrib import admin

# No models to register here
# Profile is registered in home/admin.py
