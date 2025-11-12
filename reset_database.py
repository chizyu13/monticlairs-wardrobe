#!/usr/bin/env python
"""
Script to reset database and recreate sample data
Use this if you need to start fresh
"""
import os
import sys

print("=" * 60)
print("DATABASE RESET SCRIPT")
print("=" * 60)
print("\nWARNING: This will delete ALL data in your database!")
print("This includes:")
print("- All users")
print("- All products")
print("- All categories")
print("- All orders")
print("- All checkouts")
print("\n" + "=" * 60)

response = input("\nAre you sure you want to continue? (yes/no): ")

if response.lower() != 'yes':
    print("\n❌ Operation cancelled.")
    sys.exit(0)

print("\n🔄 Flushing database...")
os.system('python manage.py flush --noinput')

print("\n🔄 Running migrations...")
os.system('python manage.py migrate')

print("\n🔄 Creating sample data...")
os.system('python setup_sample_data.py')

print("\n" + "=" * 60)
print("✅ DATABASE RESET COMPLETE!")
print("=" * 60)
print("\nLogin credentials:")
print("Username: admin")
print("Password: admin123")
print("\nRun: python manage.py runserver")
print("=" * 60)
