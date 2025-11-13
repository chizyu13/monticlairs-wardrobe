import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'montclair_wardrobe.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    if tables:
        print(f"\nFound {len(tables)} tables in database 'montclair_wardrobe':")
        print("-" * 50)
        for table in tables:
            print(f"  - {table[0]}")
    else:
        print("\nNo tables found in database 'montclair_wardrobe'")
        print("\nChecking database connection...")
        cursor.execute("SELECT DATABASE()")
        db = cursor.fetchone()
        print(f"Connected to database: {db[0]}")
