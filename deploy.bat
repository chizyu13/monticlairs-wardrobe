@echo off
echo ============================================================
echo DEPLOYING TO LIVE WEBSITE (RENDER)
echo ============================================================
echo.

echo Step 1: Adding all changes to Git...
git add .
if %errorlevel% neq 0 (
    echo ERROR: Failed to add files to Git
    pause
    exit /b 1
)
echo ✓ Files added
echo.

echo Step 2: Committing changes...
set /p commit_message="Enter commit message (or press Enter for default): "
if "%commit_message%"=="" set commit_message=Update product images and static image support

git commit -m "%commit_message%"
if %errorlevel% neq 0 (
    echo ERROR: Failed to commit changes
    echo This might mean there are no changes to commit
    pause
    exit /b 1
)
echo ✓ Changes committed
echo.

echo Step 3: Pushing to GitHub...
git push origin main
if %errorlevel% neq 0 (
    echo ERROR: Failed to push to GitHub
    echo Please check your Git credentials and internet connection
    pause
    exit /b 1
)
echo ✓ Pushed to GitHub
echo.

echo ============================================================
echo ✅ DEPLOYMENT INITIATED!
echo ============================================================
echo.
echo Next steps:
echo 1. Go to Render dashboard: https://dashboard.render.com/
echo 2. Wait for deployment to complete (2-5 minutes)
echo 3. Click on your web service
echo 4. Go to "Shell" tab
echo 5. Run: python manage.py migrate
echo 6. Run: python assign_static_images.py
echo 7. Visit your live website to verify
echo.
echo ============================================================
pause
