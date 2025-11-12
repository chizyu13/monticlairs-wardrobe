# Cloudinary Setup for Production

## Overview

Cloudinary is used for persistent image storage in production (Render deployment). Since Render's free tier uses ephemeral filesystem, uploaded images would be lost on application restart without cloud storage.

## Getting Cloudinary Credentials

1. **Sign up for Cloudinary**:
   - Go to https://cloudinary.com/
   - Create a free account (generous free tier available)
   - Verify your email

2. **Get your credentials**:
   - After logging in, go to your Dashboard
   - You'll see your credentials:
     - Cloud Name
     - API Key
     - API Secret
   - Keep these secure!

## Setting Up in Render

1. **Go to your Render Dashboard**:
   - Navigate to your web service
   - Click on "Environment" in the left sidebar

2. **Add Environment Variables**:
   Add the following environment variables with your Cloudinary credentials:
   
   ```
   CLOUDINARY_CLOUD_NAME=your_cloud_name_here
   CLOUDINARY_API_KEY=your_api_key_here
   CLOUDINARY_API_SECRET=your_api_secret_here
   ```

3. **Save and Redeploy**:
   - Click "Save Changes"
   - Render will automatically redeploy your application
   - Wait for deployment to complete

## How It Works

- **Development (DEBUG=True)**: Images are stored locally in the `media/` folder
- **Production (DEBUG=False)**: Images are automatically uploaded to and served from Cloudinary

## Testing

After setup:

1. Upload a product image via the admin interface
2. Verify the image appears on the website
3. Restart your Render service (Manual Deploy > Clear build cache & deploy)
4. Verify the image still appears (it should persist)

## Troubleshooting

### Images not uploading
- Check that environment variables are set correctly in Render
- Verify Cloudinary credentials are valid
- Check application logs for Cloudinary errors

### Images not displaying
- Ensure `django-cloudinary-storage` is in requirements.txt
- Verify `DEFAULT_FILE_STORAGE` is set in settings.py
- Check browser console for image loading errors

### Old local images not showing
- Cloudinary only handles new uploads
- Re-upload existing images through admin interface
- Or migrate existing images using Django management command

## Cost

Cloudinary free tier includes:
- 25 GB storage
- 25 GB monthly bandwidth
- 25,000 transformations per month

This is more than sufficient for most small to medium e-commerce sites.

## Alternative: AWS S3

If you prefer AWS S3 instead of Cloudinary:

1. Install `django-storages` and `boto3`
2. Configure S3 bucket and credentials
3. Update `DEFAULT_FILE_STORAGE` to use S3 backend

See Django Storages documentation for details.
