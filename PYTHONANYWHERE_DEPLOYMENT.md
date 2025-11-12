# Deploy Django to PythonAnywhere - Complete Guide

## 🎯 Why PythonAnywhere is Better

- ✅ **Free tier with Bash console** (can run commands!)
- ✅ **Persistent file storage** (images won't disappear)
- ✅ **Easy database access** (can run migrations easily)
- ✅ **Simple setup** (no complex build scripts)
- ✅ **Great for Django** (designed for Python apps)

## 📋 Prerequisites

1. GitHub account with your code pushed
2. PythonAnywhere free account (sign up at https://www.pythonanywhere.com)

## 🚀 Step-by-Step Deployment

### Step 1: Sign Up for PythonAnywhere

1. Go to https://www.pythonanywhere.com
2. Click **"Start running Python online in less than a minute!"**
3. Create a **Beginner (Free)** account
4. Verify your email

### Step 2: Open a Bash Console

1. After logging in, click **"Consoles"** tab
2. Click **"Bash"** to open a new console
3. You'll see a terminal - this is where we'll work!

### Step 3: Clone Your Repository

In the Bash console, run:

```bash
# Clone your repository
git clone https://github.com/chiz13/monticlairs-wardrobe.git

# Navigate into your project
cd monticlairs-wardrobe

# Check that files are there
ls
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub details.

### Step 4: Create a Virtual Environment

```bash
# Create virtual environment
mkvirtualenv --python=/usr/bin/python3.10 myenv

# It will automatically activate
# You should see (myenv) in your prompt
```

### Step 5: Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# This might take 2-3 minutes
```

### Step 6: Set Up Database

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Enter username: admin
# Enter email: admin@example.com
# Enter password: (your choice)

# Assign static images to products
python assign_static_images.py
```

### Step 7: Collect Static Files

```bash
# Collect static files
python manage.py collectstatic --noinput
```

### Step 8: Configure Web App

1. Go to **"Web"** tab in PythonAnywhere dashboard
2. Click **"Add a new web app"**
3. Click **"Next"** (for free domain)
4. Select **"Manual configuration"**
5. Choose **Python 3.10**
6. Click **"Next"**

### Step 9: Configure WSGI File

1. In the **Web** tab, scroll to **"Code"** section
2. Click on the **WSGI configuration file** link (blue link)
3. **Delete everything** in the file
4. **Paste this** (replace `YOUR_USERNAME` and `YOUR_REPO_NAME`):

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/YOUR_USERNAME/YOUR_REPO_NAME'
if path not in sys.path:
    sys.path.append(path)

# Set environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'montclair_wardrobe.settings'

# Activate virtual environment
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5. Click **"Save"** (top right)

### Step 10: Set Virtual Environment Path

1. Go back to **"Web"** tab
2. Scroll to **"Virtualenv"** section
3. Enter: `/home/YOUR_USERNAME/.virtualenvs/myenv`
4. Click the checkmark ✓

### Step 11: Configure Static Files

1. In **"Web"** tab, scroll to **"Static files"** section
2. Click **"Enter URL"** and add:
   - URL: `/static/`
   - Directory: `/home/YOUR_USERNAME/YOUR_REPO_NAME/staticfiles`
3. Click checkmark ✓
4. Add another:
   - URL: `/media/`
   - Directory: `/home/YOUR_USERNAME/YOUR_REPO_NAME/media`
5. Click checkmark ✓

### Step 12: Update Django Settings

In Bash console, edit settings:

```bash
cd ~/YOUR_REPO_NAME
nano montclair_wardrobe/settings.py
```

Add your PythonAnywhere domain to ALLOWED_HOSTS:

```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'YOUR_USERNAME.pythonanywhere.com']
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

Commit this change:
```bash
git add montclair_wardrobe/settings.py
git commit -m "Add PythonAnywhere domain to ALLOWED_HOSTS"
git push origin main
```

### Step 13: Reload Web App

1. Go to **"Web"** tab
2. Click the big green **"Reload YOUR_USERNAME.pythonanywhere.com"** button
3. Wait 10-20 seconds

### Step 14: Visit Your Site!

Go to: `https://YOUR_USERNAME.pythonanywhere.com`

Your site should be live! 🎉

## 🎨 Verify Everything Works

1. **Homepage** - Should show products with images
2. **Login** - Go to `/admin/` and login
3. **Images** - Should be visible on all pages
4. **Logout** - Should work without errors

## 🔧 Troubleshooting

### Site Shows "Something went wrong"

Check error logs:
1. Go to **"Web"** tab
2. Click **"Error log"** link
3. Read the error message
4. Fix the issue and reload

### Static Files Not Loading

1. Check **"Static files"** section has correct paths
2. Run in Bash console:
   ```bash
   cd ~/YOUR_REPO_NAME
   python manage.py collectstatic --noinput
   ```
3. Reload web app

### Database Errors

Run migrations in Bash console:
```bash
cd ~/YOUR_REPO_NAME
workon myenv
python manage.py migrate
```

### Images Not Showing

Assign images in Bash console:
```bash
cd ~/YOUR_REPO_NAME
workon myenv
python assign_static_images.py
```

## 🔄 Updating Your Site

When you make changes:

```bash
# In Bash console
cd ~/YOUR_REPO_NAME
git pull origin main
workon myenv
pip install -r requirements.txt  # If requirements changed
python manage.py migrate  # If models changed
python manage.py collectstatic --noinput  # If static files changed
```

Then reload web app from **"Web"** tab.

## 💡 Useful Commands

```bash
# Activate virtual environment
workon myenv

# Go to project directory
cd ~/YOUR_REPO_NAME

# Run Django shell
python manage.py shell

# Check migrations
python manage.py showmigrations

# Create new superuser
python manage.py createsuperuser

# View logs
tail -f /var/log/YOUR_USERNAME.pythonanywhere.com.error.log
```

## 📊 Free Tier Limits

PythonAnywhere free tier includes:
- ✅ 1 web app
- ✅ 512 MB disk space
- ✅ Bash console access
- ✅ MySQL database
- ✅ HTTPS included
- ⚠️ Site sleeps after inactivity (wakes on visit)
- ⚠️ Custom domain requires paid plan

## 🎯 Advantages Over Render

| Feature | PythonAnywhere Free | Render Free |
|---------|-------------------|-------------|
| Console Access | ✅ Yes | ❌ No |
| Persistent Storage | ✅ Yes | ❌ No |
| Easy Migrations | ✅ Yes | ❌ Difficult |
| Django Optimized | ✅ Yes | ⚠️ Generic |
| Setup Complexity | ✅ Easy | ❌ Complex |

## 🆘 Need Help?

If you get stuck:
1. Check PythonAnywhere error logs
2. Check Bash console for error messages
3. Visit PythonAnywhere forums
4. Check Django documentation

## 📝 Summary

PythonAnywhere is perfect for Django because:
- Easy to set up
- Has console access (can run commands!)
- Files persist (images won't disappear)
- Free tier is actually usable
- Great for development and small projects

Your site will be at: `https://YOUR_USERNAME.pythonanywhere.com`

Good luck! 🚀
