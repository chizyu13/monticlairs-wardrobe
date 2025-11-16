#!/bin/bash
# Chat Fix Deployment Script for PythonAnywhere
# Run this in your PythonAnywhere Bash console

echo "========================================="
echo "Chat System Fix Deployment"
echo "========================================="
echo ""

# Navigate to project
echo "1. Navigating to project directory..."
cd ~/monticlairs-wardrobe || exit 1

# Activate virtual environment
echo "2. Activating virtual environment..."
source venv/bin/activate || exit 1

# Pull latest changes
echo "3. Pulling latest changes from GitHub..."
git pull origin main

# Install/update dependencies
echo "4. Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "5. Running database migrations..."
python manage.py migrate

# Collect static files
echo "6. Collecting static files..."
python manage.py collectstatic --noinput

# Check for errors
echo "7. Checking for configuration errors..."
python manage.py check

# Reload web app
echo "8. Reloading web application..."
touch /var/www/chiz13_pythonanywhere_com_wsgi.py

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Visit your website and test the chat"
echo "2. Open browser DevTools (F12) to check for errors"
echo "3. If issues persist, check error log:"
echo "   tail -n 50 /var/log/chiz13.pythonanywhere.com.error.log"
echo ""
