"""
Run this script on PythonAnywhere to fix field lengths in database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'montclair_wardrobe.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Alter the phone_number column in home_checkout table
    cursor.execute("""
        ALTER TABLE home_checkout 
        MODIFY COLUMN phone_number VARCHAR(20) NOT NULL
    """)
    print("✓ Updated home_checkout.phone_number to VARCHAR(20)")
    
    # Alter the room_number column in home_checkout table (increase length)
    cursor.execute("""
        ALTER TABLE home_checkout 
        MODIFY COLUMN room_number VARCHAR(500)
    """)
    print("✓ Updated home_checkout.room_number to VARCHAR(500)")
    
    # Alter the phone_number column in home_profile table
    cursor.execute("""
        ALTER TABLE home_profile 
        MODIFY COLUMN phone_number VARCHAR(20)
    """)
    print("✓ Updated home_profile.phone_number to VARCHAR(20)")
    
    # Check if Store table exists and update it
    cursor.execute("""
        SHOW TABLES LIKE 'home_store'
    """)
    if cursor.fetchone():
        cursor.execute("""
            ALTER TABLE home_store 
            MODIFY COLUMN phone_number VARCHAR(20) NOT NULL
        """)
        print("✓ Updated home_store.phone_number to VARCHAR(20)")
    
    print("\nAll fields updated successfully!")
