# Using Static Images for Products

## What We Did

Added support for using images from your `static/images/` folders for products, so you don't have to re-upload them.

## How It Works

### 1. New Field Added
- Products now have a `static_image` field
- This stores the path to an image in your static folder
- Example: `images/Jewerly/watch1.jpg`

### 2. Smart Image Display
- Templates now use `product.get_image_url()` method
- This method checks:
  1. First: Does product have an uploaded image? (from media folder)
  2. Second: Does product have a static_image path? (from static folder)
  3. Fallback: Show default placeholder

### 3. Priority System
```
Uploaded Image (media/) > Static Image (static/) > Default Placeholder
```

## Current Status

✅ **8 products assigned static images**:
- Gold Necklace → Jewerly folder
- Kids T-Shirt → Kids folder
- Ladies Dress → Ladies-Wear folder
- Men's Suit → Mens-Wear folder
- Baby Onesie → Baby-Wear folder
- Running Shoes → Shoes folder
- Sports Jersey → Sports-Wear folder
- Luxury Watch → Watches folder

## How to Use

### Option 1: Automatic Assignment (Recommended)
Run the script to randomly assign images from category folders:
```bash
python assign_static_images.py
```

### Option 2: Manual Assignment via Admin
1. Go to admin panel: http://127.0.0.1:8000/admin/
2. Click on "Products"
3. Edit any product
4. In "Static Image Path" field, enter path like:
   - `images/Jewerly/watch1.jpg`
   - `images/Ladies-Wear/lady1.jpg`
   - `images/Mens-Wear/mens1.jpg`
5. Save

### Option 3: Upload New Image
1. Go to admin panel
2. Edit product
3. Upload image in "Product Image" field
4. This will take priority over static image

## Available Images by Category

Your static/images folder contains:

- **Jewerly**: 4 images
- **Kids**: 3 images
- **Ladies Wear**: 11 images
- **Men's Wear**: 14 images
- **Msimbi (Babies)**: 5 images
- **Shoes**: 9 images
- **Sports Wear**: 10 images
- **Watches**: 11 images

## Testing

1. Start server:
   ```bash
   python manage.py runserver
   ```

2. Visit homepage: http://127.0.0.1:8000/

3. You should see product images from your static folders!

## Admin Panel Features

In the admin panel, you can now:
- See the "Static Image Path" field
- Edit it to change which static image is used
- Upload a new image to override the static image
- Leave both empty to use default placeholder

## For Production (Render)

When deploying to Render:

1. **Static images will work** - They're part of your code
2. **Uploaded images need Cloudinary** - Follow `docs/CLOUDINARY_SETUP.md`
3. **Priority remains the same**:
   - Uploaded (Cloudinary) > Static > Default

## Troubleshooting

### Images not showing?
1. Check the static image path is correct
2. Verify image exists in static/images folder
3. Check browser console for 404 errors
4. Run: `python manage.py collectstatic`

### Want to change an image?
1. Go to admin panel
2. Edit product
3. Change "Static Image Path" field
4. Or upload new image in "Product Image" field

### Want to add more images?
1. Add images to appropriate folder in `static/images/`
2. Run `python assign_static_images.py` to reassign
3. Or manually set path in admin panel

## Benefits

✅ No need to re-upload existing images
✅ Images are part of your codebase (version controlled)
✅ Fast loading (served as static files)
✅ Easy to manage in folders
✅ Can still upload custom images when needed
✅ Works in both development and production

## Scripts Available

- `assign_static_images.py` - Assign static images to products
- `setup_sample_data.py` - Create sample products and categories
- `reset_database.py` - Reset database and recreate sample data
