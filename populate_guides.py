"""
Run this script with: python manage.py shell < populate_guides.py
"""
from home.models import PlatformGuide
from django.contrib.auth.models import User

admin = User.objects.filter(is_staff=True).first()

# Checkout Guide
PlatformGuide.objects.get_or_create(
    slug='complete-checkout-guide',
    defaults={
        'title': 'Complete Checkout Guide',
        'category': 'checkout',
        'description': 'Everything you need to know about completing your purchase.',
        'content': '<h2>Checkout Steps</h2><p>1. Review cart 2. Enter delivery info 3. Choose payment 4. Confirm order</p>',
        'featured': True,
        'display_order': 5,
        'created_by': admin,
        'is_published': True,
    }
)

# Payment Methods Guide
PlatformGuide.objects.get_or_create(
    slug='payment-methods-explained',
    defaults={
        'title': 'Payment Methods Explained',
        'category': 'checkout',
        'description': 'Learn about MTN Money, Airtel Money, and Cash on Delivery options.',
        'content': '<h2>Payment Options</h2><ul><li>MTN Mobile Money</li><li>Airtel Money</li><li>Cash on Delivery</li></ul>',
        'featured': False,
        'display_order': 6,
        'created_by': admin,
        'is_published': True,
    }
)

# Account Management Guide
PlatformGuide.objects.get_or_create(
    slug='managing-your-account',
    defaults={
        'title': 'Managing Your Account',
        'category': 'account',
        'description': 'Update profile, change password, and manage settings.',
        'content': '<h2>Account Settings</h2><p>Access your profile to update information and preferences.</p>',
        'featured': False,
        'display_order': 7,
        'created_by': admin,
        'is_published': True,
    }
)

# Order Tracking Guide
PlatformGuide.objects.get_or_create(
    slug='tracking-your-orders',
    defaults={
        'title': 'Tracking Your Orders',
        'category': 'account',
        'description': 'View order history and track delivery status.',
        'content': '<h2>Order History</h2><p>Click "My Orders" to see all your purchases and their status.</p>',
        'featured': False,
        'display_order': 8,
        'created_by': admin,
        'is_published': True,
    }
)

# Seller Guide
PlatformGuide.objects.get_or_create(
    slug='how-to-sell-on-montclair',
    defaults={
        'title': 'How to Sell on Montclair Wardrobe',
        'category': 'seller',
        'description': 'Start selling your fashion items on our platform.',
        'content': '<h2>Become a Seller</h2><p>Post products, manage inventory, and grow your business.</p>',
        'featured': False,
        'display_order': 9,
        'created_by': admin,
        'is_published': True,
    }
)

print("✅ All guides created successfully!")
print("Visit http://localhost:8000/help/ to see them")
