# Render Deployment Checklist for Montclair Wardrobe

## ✅ Pre-Deployment (DONE)
- [x] Code pushed to GitHub: https://github.com/chizyu13/monticlairs-wardrobe
- [x] requirements.txt updated with production dependencies
- [x] build.sh created
- [x] render.yaml configured
- [x] settings.py updated for production

## 📝 Step-by-Step Deployment

### STEP 1: Sign Up/Login to Render
1. Go to: https://dashboard.render.com/register
2. Sign up with GitHub (recommended) or email
3. Verify your email if needed

### STEP 2: Create PostgreSQL Database FIRST
1. Click "New +" button (top right)
2. Select "PostgreSQL"
3. Fill in:
   - **Name**: `montclair-db`
   - **Database**: `montclair_wardrobe`
   - **User**: `montclair_user`
   - **Region**: Oregon (US West) or closest to you
   - **PostgreSQL Version**: 16
   - **Plan**: Free
4. Click "Create Database"
5. **WAIT** for database to be created (takes 1-2 minutes)
6. Once created, click on the database
7. Scroll down to "Connections"
8. **COPY** the "Internal Database URL" (starts with postgres://)
   - Example: `postgres://montclair_user:xxxxx@dpg-xxxxx/montclair_wardrobe`
9. **SAVE THIS URL** - you'll need it in Step 3!

### STEP 3: Create Web Service
1. Click "New +" button
2. Select "Web Service"
3. Click "Connect a repository"
4. If not connected, click "Connect GitHub"
5. Find and select: `chizyu13/monticlairs-wardrobe`
6. Click "Connect"

### STEP 4: Configure Web Service
Fill in these settings:

**Basic Settings:**
- **Name**: `montclair-wardrobe` (or any name you like)
- **Region**: Same as your database (Oregon US West)
- **Branch**: `main`
- **Runtime**: Python 3
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn montclair_wardrobe.wsgi:application`

**Instance Type:**
- **Plan**: Free

### STEP 5: Add Environment Variables
Click "Advanced" → "Add Environment Variable"

Add these variables ONE BY ONE:

1. **SECRET_KEY**
   ```
   =ye^t7i3^$11ty0tjf5o6=@t*3rk73(j2x_*4dkrq!potlu(2!
   ```

2. **DEBUG**
   ```
   False
   ```

3. **DATABASE_URL**
   ```
   [PASTE THE INTERNAL DATABASE URL FROM STEP 2]
   ```

4. **STRIPE_SECRET_KEY** (your Stripe secret key)
   ```
   sk_test_51RF8Qg4fsNGmT5PiLlT64QiXrpzO7F83qdYfbywV0bjDrQQVa09QXCGNjYECk2B1IKsrQYGxjfkfdxe2R5Iz7YLz00ZAtw0xiF
   ```

5. **STRIPE_PUBLISHABLE_KEY** (your Stripe publishable key)
   ```
   pk_test_[your_key_here]
   ```

6. **MTN_API_USER** (optional - add if you have it)
   ```
   your_mtn_api_user
   ```

7. **MTN_API_KEY** (optional)
   ```
   your_mtn_api_key
   ```

8. **MTN_SUBSCRIPTION_KEY** (optional)
   ```
   your_mtn_subscription_key
   ```

9. **AIRTEL_CLIENT_ID** (optional)
   ```
   your_airtel_client_id
   ```

10. **AIRTEL_CLIENT_SECRET** (optional)
    ```
    your_airtel_client_secret
    ```

### STEP 6: Deploy!
1. Click "Create Web Service"
2. Render will start building your app
3. Watch the logs - it will:
   - Install dependencies (2-3 minutes)
   - Run migrations
   - Collect static files
   - Start the server

### STEP 7: Wait for Deployment
- First deployment takes 5-10 minutes
- Watch the logs for any errors
- When you see "Live" with a green dot, it's ready!

### STEP 8: Access Your Site
Your site will be at:
```
https://montclair-wardrobe.onrender.com
```
(or whatever name you chose)

### STEP 9: Create Superuser
1. In your web service dashboard, click "Shell" tab
2. Run this command:
   ```bash
   python manage.py createsuperuser
   ```
3. Follow the prompts to create admin account
4. Access admin at: `https://your-site.onrender.com/admin`

## 🚨 Common Issues & Solutions

### Build Fails
- Check the logs for specific errors
- Make sure all dependencies are in requirements.txt
- Verify build.sh has correct commands

### Database Connection Error
- Make sure DATABASE_URL is correct
- Check database is in same region as web service
- Verify database is active (not suspended)

### Static Files Not Loading
- Check STATIC_ROOT in settings.py
- Verify WhiteNoise is in MIDDLEWARE
- Run `python manage.py collectstatic` in Shell

### App Keeps Sleeping (Free Tier)
- Free tier sleeps after 15 minutes of inactivity
- Takes ~30 seconds to wake up on first request
- Upgrade to paid plan ($7/month) for always-on

## 📊 After Deployment

### Monitor Your App
- View logs in Render dashboard
- Set up email alerts for failures
- Monitor database usage

### Update Your App
To deploy updates:
```bash
git add .
git commit -m "Your update message"
git push origin main
```
Render will automatically redeploy!

### Custom Domain (Optional)
1. Go to your web service settings
2. Click "Custom Domain"
3. Add your domain
4. Update DNS records as instructed

## 🎉 Success Checklist
- [ ] Database created and active
- [ ] Web service deployed successfully
- [ ] Site loads at your Render URL
- [ ] Admin panel accessible
- [ ] Superuser created
- [ ] Can login and browse products
- [ ] Static files loading correctly
- [ ] Database working (can create/edit data)

## 📞 Need Help?
- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/

---

**Your GitHub Repo**: https://github.com/chizyu13/monticlairs-wardrobe
**Your SECRET_KEY**: =ye^t7i3^$11ty0tjf5o6=@t*3rk73(j2x_*4dkrq!potlu(2!

Good luck! 🚀
