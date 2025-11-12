ibn # Montclair Wardrobe - Render Deployment Guide

## Prerequisites
1. GitHub account
2. Render account (sign up at https://render.com)
3. Your project pushed to GitHub

## Step-by-Step Deployment

### 1. Push Your Code to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for Render deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/montclair-wardrobe.git
git branch -M main
git push -u origin main
```

### 2. Create PostgreSQL Database on Render

1. Go to https://dashboard.render.com
2. Click "New +" → "PostgreSQL"
3. Fill in:
   - **Name**: `montclair-db`
   - **Database**: `montclair_wardrobe`
   - **User**: `montclair_user`
   - **Region**: Choose closest to your users
   - **Plan**: Free
4. Click "Create Database"
5. **Save the connection details** (you'll need them)

### 3. Create Web Service on Render

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Fill in:
   - **Name**: `montclair-wardrobe`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Runtime**: Python
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn montclair_wardrobe.wsgi:application`
   - **Plan**: Free

### 4. Add Environment Variables

In the "Environment" section, add:

```
SECRET_KEY=your-secret-key-here-generate-a-new-one
DEBUG=False
DATABASE_URL=<your-postgres-connection-string>
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
MTN_API_USER=your-mtn-api-user
MTN_API_KEY=your-mtn-api-key
MTN_SUBSCRIPTION_KEY=your-mtn-subscription-key
AIRTEL_CLIENT_ID=your-airtel-client-id
AIRTEL_CLIENT_SECRET=your-airtel-client-secret
```

**Generate a new SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Install dependencies
   - Run migrations
   - Collect static files
   - Start your application

### 6. Create Superuser

After deployment, go to the "Shell" tab in your Render dashboard and run:

```bash
python manage.py createsuperuser
```

### 7. Access Your Site

Your site will be available at:
`https://montclair-wardrobe.onrender.com`

Admin panel:
`https://montclair-wardrobe.onrender.com/admin`

## Important Notes

### Free Tier Limitations
- App sleeps after 15 minutes of inactivity
- Takes ~30 seconds to wake up on first request
- 750 hours/month free (enough for one app)
- Database expires after 90 days of inactivity

### Media Files (Product Images)
The free tier doesn't persist uploaded files. For production, you need to:

1. **Use Cloudinary (Recommended - Free tier available)**
   ```bash
   pip install django-cloudinary-storage
   ```

2. **Or AWS S3**
   ```bash
   pip install django-storages boto3
   ```

Add to `requirements.txt` and configure in `settings.py`

### Custom Domain
1. Go to your web service settings
2. Click "Custom Domain"
3. Add your domain
4. Update DNS records as instructed

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify `build.sh` has execute permissions

### Database Connection Issues
- Verify `DATABASE_URL` environment variable
- Check database is in same region as web service

### Static Files Not Loading
- Run `python manage.py collectstatic` manually in Shell
- Check `STATIC_ROOT` and `STATIC_URL` settings

### App Keeps Sleeping
- Upgrade to paid plan ($7/month) for always-on service
- Or use a service like UptimeRobot to ping your site every 5 minutes

## Monitoring

- View logs in Render dashboard
- Set up email alerts for deployment failures
- Monitor database usage

## Updating Your App

```bash
# Make changes locally
git add .
git commit -m "Your update message"
git push origin main
```

Render will automatically redeploy!

## Support

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
