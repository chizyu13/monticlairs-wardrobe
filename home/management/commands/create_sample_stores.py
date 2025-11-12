from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from home.models import Store


class Command(BaseCommand):
    help = 'Create sample store locations in Lusaka'

    def handle(self, *args, **kwargs):
        # Use the first superuser as manager, or None if no users exist
        manager = User.objects.filter(is_superuser=True).first()
        
        if not manager:
            # Use any staff user
            manager = User.objects.filter(is_staff=True).first()
        
        if manager:
            self.stdout.write(self.style.SUCCESS(f'Using manager: {manager.username}'))
        else:
            self.stdout.write(self.style.WARNING('No manager user found. Stores will be created without a manager.'))

        # Sample stores in Lusaka
        stores_data = [
            {
                'name': 'Montclair Boutique - City Center',
                'address': 'Cairo Road, Shop 45, Levy Junction Mall',
                'city': 'Lusaka',
                'latitude': -15.4167,
                'longitude': 28.2833,
                'phone_number': '+260971234567',
                'whatsapp_number': '+260971234567',
                'email': 'citycenter@montclairwardrobe.com',
                'opening_hours': 'Mon-Fri: 9:00 AM - 6:00 PM\nSat: 10:00 AM - 5:00 PM\nSun: Closed',
                'is_active': True,
                'is_pickup_point': True,
                'manager': manager
            },
            {
                'name': 'Montclair Wardrobe - Manda Hill',
                'address': 'Manda Hill Shopping Mall, Ground Floor',
                'city': 'Lusaka',
                'latitude': -15.3875,
                'longitude': 28.3228,
                'phone_number': '+260972345678',
                'whatsapp_number': '+260972345678',
                'email': 'mandahill@montclairwardrobe.com',
                'opening_hours': 'Mon-Sun: 9:00 AM - 8:00 PM',
                'is_active': True,
                'is_pickup_point': True,
                'manager': manager
            },
            {
                'name': 'Montclair Fashion - East Park Mall',
                'address': 'East Park Mall, Shop 23',
                'city': 'Lusaka',
                'latitude': -15.3929,
                'longitude': 28.3850,
                'phone_number': '+260973456789',
                'whatsapp_number': '+260973456789',
                'email': 'eastpark@montclairwardrobe.com',
                'opening_hours': 'Mon-Sat: 9:00 AM - 7:00 PM\nSun: 10:00 AM - 5:00 PM',
                'is_active': True,
                'is_pickup_point': True,
                'manager': manager
            },
            {
                'name': 'Montclair Outlet - Woodlands',
                'address': 'Woodlands Shopping Centre, Unit 12',
                'city': 'Lusaka',
                'latitude': -15.4369,
                'longitude': 28.3475,
                'phone_number': '+260974567890',
                'whatsapp_number': '+260974567890',
                'email': 'woodlands@montclairwardrobe.com',
                'opening_hours': 'Mon-Fri: 9:00 AM - 6:00 PM\nSat: 9:00 AM - 4:00 PM\nSun: Closed',
                'is_active': True,
                'is_pickup_point': True,
                'manager': manager
            },
            {
                'name': 'Montclair Store - Arcades',
                'address': 'Arcades Shopping Mall, First Floor',
                'city': 'Lusaka',
                'latitude': -15.3947,
                'longitude': 28.3053,
                'phone_number': '+260975678901',
                'whatsapp_number': '+260975678901',
                'email': 'arcades@montclairwardrobe.com',
                'opening_hours': 'Mon-Sun: 9:00 AM - 8:00 PM',
                'is_active': True,
                'is_pickup_point': True,
                'manager': manager
            }
        ]

        created_count = 0
        updated_count = 0

        for store_data in stores_data:
            store, created = Store.objects.update_or_create(
                name=store_data['name'],
                defaults=store_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created store: {store.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated store: {store.name}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nSummary: {created_count} stores created, {updated_count} stores updated'
        ))
