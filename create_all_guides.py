"""
Script to create comprehensive user guides for Montclair Wardrobe
Run with: python manage.py shell < create_all_guides.py
"""

from home.models import PlatformGuide
from django.contrib.auth.models import User

# Get admin user
admin = User.objects.filter(is_staff=True).first()

if not admin:
    print("❌ No admin user found. Please create an admin user first.")
    exit()

# Clear existing guides (optional - comment out if you want to keep existing)
# PlatformGuide.objects.all().delete()

guides_data = [
    {
        'title': 'Getting Started with Montclair Wardrobe',
        'category': 'getting_started',
        'description': 'Welcome to Montclair Wardrobe! Learn the basics of using our platform.',
        'content': '''
        <h2>Welcome to Montclair Wardrobe! 👋</h2>
        <p>Thank you for choosing Montclair Wardrobe for your fashion needs. This guide will help you get started.</p>
        
        <h3>What is Montclair Wardrobe?</h3>
        <p>Montclair Wardrobe is Zambia's premier online fashion marketplace where you can:</p>
        <ul>
            <li>Browse a curated collection of quality fashion items</li>
            <li>Shop securely with multiple payment options</li>
            <li>Get items delivered to your doorstep</li>
            <li>Sell your own fashion items</li>
        </ul>
        
        <h3>Quick Start Steps</h3>
        <ol>
            <li><strong>Create an Account</strong> - Register to start shopping</li>
            <li><strong>Browse Products</strong> - Explore our boutique collection</li>
            <li><strong>Add to Cart</strong> - Select items you love</li>
            <li><strong>Checkout</strong> - Complete your purchase securely</li>
        </ol>
        
        <h3>Need Help?</h3>
        <p>Browse our other guides or contact our support team anytime!</p>
        ''',
        'featured': True,
        'display_order': 1,
    },
]

    {
        'title': 'How to Create an Account',
        'category': 'getting_started',
        'description': 'Step-by-step guide to registering and setting up your account.',
        'content': '''
        <h2>Creating Your Account</h2>
        <p>Follow these simple steps to create your Montclair Wardrobe account:</p>
        
        <h3>Registration Process</h3>
        <ol>
            <li>Click the "Register" button in the top navigation</li>
            <li>Fill in your details:
                <ul>
                    <li>Username (unique identifier)</li>
                    <li>Email address</li>
                    <li>Password (minimum 8 characters)</li>
                    <li>Confirm password</li>
                </ul>
            </li>
            <li>Click "Create Account"</li>
            <li>You'll be automatically logged in</li>
        </ol>
        
        <h3>Setting Up Your Profile</h3>
        <p>After registration, complete your profile:</p>
        <ol>
            <li>Click your username in the navigation</li>
            <li>Select "My Profile"</li>
            <li>Add your information:
                <ul>
                    <li>Profile picture</li>
                    <li>Bio</li>
                    <li>Location</li>
                    <li>Phone number (for deliveries)</li>
                </ul>
            </li>
            <li>Click "Save Changes"</li>
        </ol>
        
        <h3>Account Security</h3>
        <p><strong>Tips for a secure account:</strong></p>
        <ul>
            <li>Use a strong, unique password</li>
            <li>Don't share your login credentials</li>
            <li>Change your password regularly</li>
            <li>Log out on shared devices</li>
        </ul>
        ''',
        'featured': False,
        'display_order': 2,
    },

    {
        'title': 'Browsing and Searching for Products',
        'category': 'shopping',
        'description': 'Learn how to find the perfect items using our search and filter features.',
        'content': '''
        <h2>Finding What You Love</h2>
        <p>Discover amazing fashion items with our easy-to-use browsing tools.</p>
        
        <h3>Browse by Category</h3>
        <p>On the homepage, you'll find product categories:</p>
        <ul>
            <li>Click any category card to see items in that category</li>
            <li>Categories include: Jewelry, Clothing, Accessories, and more</li>
        </ul>
        
        <h3>View All Products</h3>
        <ol>
            <li>Click "Boutique" in the navigation menu</li>
            <li>Browse through all available products</li>
            <li>Scroll to see more items</li>
        </ol>
        
        <h3>Product Details</h3>
        <p>Click any product to see:</p>
        <ul>
            <li>High-quality product images</li>
            <li>Detailed description</li>
            <li>Price in ZMW (Zambian Kwacha)</li>
            <li>Stock availability</li>
            <li>Customer reviews and ratings</li>
            <li>Seller information</li>
        </ul>
        
        <h3>Product Reviews</h3>
        <p>Make informed decisions by reading customer reviews:</p>
        <ul>
            <li>See star ratings (1-5 stars)</li>
            <li>Read detailed review comments</li>
            <li>Check verified purchase badges</li>
            <li>View rating distribution</li>
        </ul>
        ''',
        'featured': True,
        'display_order': 3,
    },

    {
        'title': 'Adding Items to Your Cart',
        'category': 'shopping',
        'description': 'Learn how to add products to your cart and manage your selections.',
        'content': '''
        <h2>Shopping Cart Guide</h2>
        <p>Your cart is where you collect items before checkout.</p>
        
        <h3>Adding Products</h3>
        <ol>
            <li>Browse to a product you like</li>
            <li>Click the "Add to Cart" button</li>
            <li>You'll see a confirmation message</li>
            <li>The cart icon will show your item count</li>
        </ol>
        
        <h3>Viewing Your Cart</h3>
        <ol>
            <li>Click the shopping cart icon in the navigation</li>
            <li>You'll see all items in your cart with:
                <ul>
                    <li>Product image and name</li>
                    <li>Price per item</li>
                    <li>Quantity selector</li>
                    <li>Subtotal for each item</li>
                </ul>
            </li>
        </ol>
        
        <h3>Managing Cart Items</h3>
        <p><strong>Update Quantity:</strong></p>
        <ul>
            <li>Use the + and - buttons to adjust quantity</li>
            <li>Prices update automatically</li>
        </ul>
        
        <p><strong>Remove Items:</strong></p>
        <ul>
            <li>Click the "Remove" button next to any item</li>
            <li>Confirm the removal</li>
        </ul>
        
        <h3>Cart Total</h3>
        <p>At the bottom of your cart, you'll see:</p>
        <ul>
            <li>Subtotal (sum of all items)</li>
            <li>Delivery fee (calculated at checkout)</li>
            <li>Grand total</li>
        </ul>
        
        <h3>Ready to Checkout?</h3>
        <p>Click the "Proceed to Checkout" button when you're ready to complete your purchase.</p>
        ''',
        'featured': False,
        'display_order': 4,
    },
