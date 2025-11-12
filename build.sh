#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Install dependencies (skip pip upgrade to save time)
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Assign static images to products (if script exists)
echo "Assigning static images to products..."
if [ -f "assign_static_images.py" ]; then
    python assign_static_images.py || echo "Image assignment skipped or failed"
else
    echo "assign_static_images.py not found, skipping..."
fi

echo "Build complete!"
