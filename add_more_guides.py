"""
Quick script to add more user guides
Run on PythonAnywhere: python manage.py shell < add_more_guides.py
"""

from home.models import PlatformGuide
from django.contrib.auth.models import User

# Get admin user
admin = User.objects.filter(is_staff=True).first()

if not admin:
    print("❌ No admin user found.")
    exit()

print("📚 Adding user guides...")

# Check existing guides
existing = PlatformGuide.objects.count()
print(f"Current guides: {existing}")

# Add guides if they don't exist
guides = [
    {
        'title': 'How to Create an Account',
        'slug': 'how-to-create-account',
        'category': 'getting_started',
        'description': 'Step-by-step guide to registering your account',
        'content': '<h2>Creating Your Account</h2><p>Click Register, fill in your details, and start shopping!</p>',
        'is_published': True,
        'featured': False,
        'display_order': 2,
    },
    {
        'title': 'Browsing Products',
        'slug': 'browsing-products',
        'category': 'shopping',
        'description': 'Learn how to find products',
        'content': '<h2>Finding Products</h2><p>Browse by category or use the Boutique page to see all items.</p>',
        'is_published': True,
        'featured': True,
        'display_order': 3,
    },
    {
        'title': 'Adding Items to Cart',
        'slug': 'adding-to-cart',
        'category': 'shopping',
        'description': 'How to add products to your shopping cart',
        'content': '<h2>Shopping Cart</h2><p>Click "Add to Cart" on any product. View your cart by clicking the cart icon.</p>',
        'is_published': True,
        'featured': False,
        'display_order': 4,
    },
    {
        'title': 'Checkout Process',
        'slug': 'checkout-process',
        'category': 'checkout',
        'description': 'Complete your purchase step by step',
        'content': '<h2>Completing Your Order</h2><p>Provide delivery details, choose payment method, and confirm your order.</p>',
        'is_published': True,
        'featured': True,
        'display_order': 5,
    },
    {
        'title': 'Payment Methods',
        'slug': 'payment-methods',
        'category': 'checkout',
        'description': 'Available payment options',
        'content': '<h2>How to Pay</h2><p>We accept MTN Mobile Money, Airtel Money, and Cash on Delivery.</p>',
        'is_published': True,
        'featured': False,
        'display_order': 6,
    },
    {
        'title': 'Tracking Your Order',
        'slug': 'tracking-order',
        'category': 'shopping',
        'description': 'Check your order status',
        'content': '<h2>Order Tracking</h2><p>View your orders in "My Orders" section. Check status and delivery updates.</p>',
        'is_published': True,
        'featured': False,
        'display_order': 7,
    },
    {
        'title': 'Writing Product Reviews',
        'slug': 'writing-reviews',
        'category': 'shopping',
        'description': 'Share your experience with products',
        'content': '<h2>Leave a Review</h2><p>After purchasing, you can rate and review products to help other shoppers.</p>',
        'is_published': True,
        'featured': False,
        'display_order': 8,
    },
    {
        'title': 'Becoming a Seller',
        'slug': 'becoming-seller',
        'category': 'account',
        'description': 'Start selling your products',
        'content': '<h2>Sell on Montclair</h2><p>Register, post your products, and start earning. We handle payments and delivery.</p>',
        'is_published': True,
        'featured': True,
        'display_order': 9,
    },
    {
        'title': 'Managing Your Products',
        'slug': 'managing-products',
        'category': 'account',
        'description': 'Edit and update your listings',
        'content': '<h2>Product Management</h2><p>Access "My Products" to edit, update stock, or remove your listings.</p>',
        'is_published': True,
        'featured': False,
        'display_order': 10,
    },
    {
        'title': 'Account Security',
        'slug': 'account-security',
        'category': 'account',
        'description': 'Keep your account safe',
        'content': '<h2>Security Tips</h2><p>Use strong passwords, don\'t share credentials, and log out on shared devices.</p>',
        'is_published': True,
        'featured': False,
        'display_order': 11,
    },
]

created_count = 0
for guide_data in guides:
    # Check if guide already exists
    if not PlatformGuide.objects.filter(slug=guide_data['slug']).exists():
        PlatformGuide.objects.create(**guide_data)
        created_count += 1
        print(f"✅ Created: {guide_data['title']}")
    else:
        print(f"⏭️  Skipped (exists): {guide_data['title']}")

print(f"\n🎉 Done! Created {created_count} new guides.")
print(f"📊 Total guides now: {PlatformGuide.objects.count()}")
