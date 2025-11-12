# Deploy to Render Free Tier (Without Shell Access)

## Problem
Render's free tier doesn't have Shell access, so we can't run commands manually after deployment.

## Solution
I've updated `build.sh` to automatically:
1. Run migrations
2. Assign static images to products
3. Everything happens during deployment!

## Deploy Now

### Step 1: Commit Changes
```bash
git add build.sh DEPLOY_WITHOUT_SHELL.md
git commit -m "Auto-assign images during deployment for free tier"
git push origin main
```

### Step 2: Wait for Deployment
1. Go to https://dashboard.render.com/
2. Render will auto-deploy (10-15 minutes)
3. Watch the logs - you should see:
   - "Running migrations..."
   - "Assigning static images to products..."
   - "✓ Updated 8 products with static images!"

### Step 3: Verify
1. Visit your live website
2. Refresh the page (Ctrl+F5)
3. Images should now appear!

## What Happens During Deployment

The build script now automatically:
- ✅ Installs dependencies
- ✅ Collects static files
- ✅ Runs database migrations (adds static_image field)
- ✅ Assigns images from static folders to products
- ✅ Everything is ready when deployment completes!

## If Images Still Don't Show

### Option 1: Manual Assignment via Admin Panel
1. Go to: `https://your-site.onrender.com/admin/`
2. Login with your admin credentials
3. Click **Products**
4. Edit each product
5. In **"Static Image Path"** field, paste:

**For each product:**
- Gold Necklace: `images/Jewerly/0d5d2674f35f4ab1c6c97711865f5601.jpg`
- Kids T-Shirt: `images/Kids/333d21f2984944b87178b7b02d014922.jpg`
- Ladies Dress: `images/Ladies-Wear/IMG-20251029-WA0012.jpg`
- Men's Suit: `images/Mens-Wear/IMG-20251028-WA0246.jpg`
- Baby Onesie: `images/Baby-Wear/baby1.jpg`
- Running Shoes: `images/Shoes/e74a704bdca1ff65c00bb732cd330619.jpg`
- Sports Jersey: `images/Sports-Wear/c7bbb4e65c04d8ab731615c376600c83.jpg`
- Luxury Watch: `images/Watches/fad625423343d65b47ed0eb8464e284f.jpg`

6. Save each product

### Option 2: Check Deployment Logs
1. In Render dashboard, click your service
2. Click "Logs" tab
3. Look for errors during image assignment
4. If you see errors, let me know what they say

## Why This Works

**Before:** Needed Shell access to run commands after deployment
**After:** Commands run automatically during build process
**Result:** Works perfectly on Render free tier!

## Benefits

✅ No Shell access needed
✅ Automatic setup on every deployment
✅ Images assigned automatically
✅ Works on free tier
✅ One-time setup, works forever

## Next Deployment

From now on, every time you deploy:
1. Push to GitHub
2. Render auto-deploys
3. Images are automatically assigned
4. Everything just works!

## Summary

Just run:
```bash
git add build.sh
git commit -m "Auto-assign images during deployment"
git push origin main
```

Then wait 10-15 minutes for deployment to complete. Your images will appear automatically!
