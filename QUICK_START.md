# Quick Start Guide - Montclair Wardrobe

## ✅ What's Been Set Up

Your e-commerce site now has:
- ✅ Product image display fixed
- ✅ Static images from folders automatically assigned
- ✅ Admin user created
- ✅ 8 sample products with images
- ✅ 8 categories configured
- ✅ Cloudinary support for production

## 🚀 Start Using Your Site

### 1. Start the Development Server
```bash
python manage.py runserver
```

### 2. Access Your Site
- **Homepage**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

### 3. Login Credentials
```
Username: admin
Password: admin123
```

## 📸 Product Images

### Current Setup
All 8 products now have images from your `static/images/` folders:
- Gold Necklace (Jewerly)
- Kids T-Shirt (Kids)
- Ladies Dress (Ladies Wear)
- Men's Suit (Men's Wear)
- Baby Onesie (Babies)
- Running Shoes (Shoes)
- Sports Jersey (Sports Wear)
- Luxury Watch (Watches)

### How Images Work
1. **Uploaded images** (via admin) take priority
2. **Static images** (from folders) are used if no upload
3. **Default placeholder** shows if neither exists

### Change Product Images

**Option A: Use Different Static Image**
1. Go to admin panel
2. Edit product
3. Change "Static Image Path" field
4. Example: `images/Watches/watch1.jpg`

**Option B: Upload New Image**
1. Go to admin panel
2. Edit product
3. Upload in "Product Image" field
4. This overrides static image

**Option C: Reassign All Images**
```bash
python assign_static_images.py
```

## 📁 Available Images

Your `static/images/` folder contains:
- **Jewerly**: 4 images
- **Kids**: 3 images
- **Ladies Wear**: 11 images
- **Men's Wear**: 14 images
- **Babies**: 5 images
- **Shoes**: 9 images
- **Sports Wear**: 10 images
- **Watches**: 11 images

## 🛠️ Useful Scripts

### Reset Everything
```bash
python reset_database.py
```
Deletes all data and recreates sample products/categories

### Assign Static Images
```bash
python assign_static_images.py
```
Randomly assigns images from category folders to products

### Create Sample Data
```bash
python setup_sample_data.py
```
Creates 8 categories and 8 sample products

## 📚 Documentation Files

- **LOGIN_CREDENTIALS.txt** - Login info and database status
- **STATIC_IMAGES_GUIDE.md** - Complete guide for using static images
- **DEPLOYMENT_GUIDE.md** - How to deploy to Render
- **CLOUDINARY_SETUP.md** - Setting up persistent image storage

## 🌐 Deploy to Production

### Quick Deploy Steps
1. Commit changes:
   ```bash
   git add .
   git commit -m "Add static image support"
   git push origin main
   ```

2. Render auto-deploys (wait 2-5 minutes)

3. Run migration on Render:
   - Go to Render Dashboard → Shell
   - Run: `python manage.py migrate`

4. Set up Cloudinary (optional but recommended):
   - See `docs/CLOUDINARY_SETUP.md`

## 🎯 Next Steps

### Add More Products
1. Login to admin panel
2. Go to Products → Add Product
3. Fill in details
4. Either:
   - Upload an image, OR
   - Set static image path (e.g., `images/Shoes/shoe1.jpg`)
5. Set status to "Active" and approval to "Approved"
6. Save

### Customize Categories
1. Login to admin panel
2. Go to Categories
3. Edit any category
4. Upload category image
5. Change icon (Font Awesome class)
6. Save

### Manage Orders
1. Login to admin panel
2. Go to Orders or Checkouts
3. View customer orders
4. Update order status
5. Mark payments as complete

## 🆘 Troubleshooting

### Can't Login?
- Username: `admin`
- Password: `admin123`
- If still fails, run: `python reset_database.py`

### Images Not Showing?
1. Check static image path is correct
2. Run: `python manage.py collectstatic`
3. Check browser console for errors
4. Verify image exists in static/images folder

### Products Not Showing?
1. Check product status is "Active"
2. Check approval_status is "Approved"
3. Check stock is > 0
4. Run: `python manage.py check`

### Database Issues?
```bash
python reset_database.py
```
This will reset everything and recreate sample data

## 📞 Support

If you encounter issues:
1. Check the relevant documentation file
2. Run `python manage.py check` for errors
3. Check browser console for JavaScript errors
4. Review server logs for Python errors

## 🎉 You're All Set!

Your e-commerce site is ready to use with:
- ✅ Working product images from static folders
- ✅ Admin panel for management
- ✅ Sample products and categories
- ✅ Ready for production deployment

Start the server and visit http://127.0.0.1:8000/ to see it in action!
