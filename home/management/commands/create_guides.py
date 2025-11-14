from django.core.management.base import BaseCommand
from home.models import PlatformGuide
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create comprehensive user guides for the platform'

    def handle(self, *args, **kwargs):
        admin = User.objects.filter(is_staff=True).first()
        
        if not admin:
            self.stdout.write(self.style.ERROR('No admin user found'))
            return
        
        guides = [
            {
                'title': 'Complete Checkout Process Guide',
                'category': 'checkout',
                'description': 'Step-by-step instructions for completing your purchase.',
                'content': '''
                <h2>Checkout Process</h2>
                <h3>Step 1: Review Your Cart</h3>
                <p>Before checkout, verify all items and quantities are correct.</p>
                
                <h3>Step 2: Enter Delivery Information</h3>
                <ul>
                    <li>Select delivery area (Inside/Outside Lusaka)</li>
                    <li>Enter street address or building name</li>
                    <li>Add delivery instructions</li>
                    <li>Provide phone number</li>
                    <li>Enter GPS location</li>
                </ul>
                
                <h3>Step 3: Choose Payment Method</h3>
                <p>Available options:</p>
                <ul>
                    <li>MTN Mobile Money</li>
                    <li>Airtel Money</li>
                    <li>Cash on Delivery</li>
                </ul>
                
                <h3>Step 4: Confirm Order</h3>
                <p>Review all details and click "Place Order".</p>
                ''',
                'featured': True,
                'display_order': 5,
            },
        ]
