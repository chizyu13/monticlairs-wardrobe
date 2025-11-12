# Deploy Static Images to Live Website

## Step-by-Step Deployment

### Step 1: Commit Your Changes to Git

Open your terminal and run these commands:

```bash
# Add all changes
git add .

# Commit with a message
git commit -m "Add static image support for products"

# Push to GitHub
git push origin main
```

### Step 2: Wait for Render to Deploy

1. Go to your Render dashboard: https://dashboard.render.com/
2. Click on your web service
3. You'll see "Deploy in progress..." 
4. Wait 2-5 minutes for deployment to complete
5. Look for "Live" status with green checkmark

### Step 3: Run Migration on Render

After deployment completes, you need to run the database migration:

**Option A: Using Render Shell (Recommended)**
1. In Render dashboard, click on your web service
2. Click "Shell" tab at the top
3. Type this command and press Enter:
   ```bash
   python manage.py migrate
   ```
4. Wait for it to complete

**Option B: Using Manual Deploy**
1. In Render dashboard, go to your web service
2. Click "Manual Deploy" dropdown
3. Select "Deploy latest commit"
4. Wait for deployment

### Step 4: Assign Static Images to Products

You have two options:

**Option A: Via Render Shell (Quick)**
1. In Render Shell, run:
   ```bash
   python assign_static_images.py
   ```
2. This will assign images from your static folders to all products

**Option B: Via Admin Panel (Manual)**
1. Go to your live admin panel: https://your-site.onrender.com/admin/
2. Login with your production credentials
3. Go to Products
4. Edit each product
5. In "Static Image Path" field, enter paths like:
   - `images/Jewerly/watch1.jpg`
   - `images/Ladies-Wear/lady1.jpg`
   - `images/Mens-Wear/mens1.jpg`
6. Save each product

### Step 5: Verify It Works

1. Visit your live website: https://your-site.onrender.com/
2. Check if product images are showing
3. Browse different categories
4. Check product detail pages

## Important Notes

### About Static Images on Render

✅ **Static images WILL work** because:
- They're part of your code repository
- Render serves static files automatically
- No Cloudinary needed for static images

### About Uploaded Images

⚠️ **Uploaded images need Cloudinary** because:
- Render's filesystem is ephemeral
- Uploaded files are lost on restart
- Follow `docs/CLOUDINARY_SETUP.md` for setup

### Priority System

Your site will use images in this order:
1. **Uploaded images** (from Cloudinary in production)
2. **Static images** (from static/images folders)
3. **Default placeholder** (if neither exists)

## Troubleshooting

### "git push" fails?

If you get authentication errors:
```bash
# Set up your GitHub credentials
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"

# Try push again
git push origin main
```

### Render deployment fails?

1. Check Render logs for errors
2. Look for Python errors or missing dependencies
3. Verify all files are committed to Git
4. Try "Clear build cache & deploy"

### Migration fails on Render?

If migration command fails:
1. Check that deployment completed successfully
2. Verify you're in the Shell tab
3. Try running: `python manage.py showmigrations`
4. Then: `python manage.py migrate home`

### Images still not showing?

1. Check browser console for 404 errors
2. Verify image paths are correct
3. Run in Render Shell: `python manage.py collectstatic --noinput`
4. Check that static files are being served

### Can't access Render Shell?

1. Make sure deployment is complete (green "Live" status)
2. Refresh the Render dashboard page
3. Try clicking Shell tab again
4. If still fails, use Manual Deploy option

## Quick Command Reference

```bash
# Local: Commit and push
git add .
git commit -m "Your message"
git push origin main

# Render Shell: Run migration
python manage.py migrate

# Render Shell: Assign images
python assign_static_images.py

# Render Shell: Collect static files
python manage.py collectstatic --noinput

# Render Shell: Check migrations
python manage.py showmigrations
```

## What Happens After Deployment

1. ✅ Your live site will have the new `static_image` field
2. ✅ Products can use images from static folders
3. ✅ Templates will use the new `get_image_url()` method
4. ✅ Admin panel will show "Static Image Path" field
5. ✅ Images will display on your live website

## Need Help?

If you encounter issues:
1. Check Render deployment logs
2. Check Render application logs
3. Verify all changes are committed to Git
4. Make sure migration ran successfully
5. Check that static files are collected

## Summary

To deploy to your live website:
1. ✅ Commit changes: `git add . && git commit -m "message" && git push`
2. ✅ Wait for Render to deploy (2-5 minutes)
3. ✅ Run migration in Render Shell: `python manage.py migrate`
4. ✅ Assign images in Render Shell: `python assign_static_images.py`
5. ✅ Visit your live site to verify

Your live website will then show product images from your static folders!
