# Live Chat Fix Summary

## Problem
Chat system showing "Failed to send message. Please try again." on PythonAnywhere (chiz13.pythonanywhere.com).

## Root Causes Identified

1. **Missing CSRF Tokens**: JavaScript wasn't sending CSRF tokens with POST requests
2. **Static Files Not Collected**: Chat widget JS/CSS files may not be in staticfiles directory
3. **URL Path Issues**: Inconsistent URL formatting in fetch calls
4. **Poor Error Handling**: No detailed error logging to identify issues

## Changes Made

### 1. Fixed CSRF Token Handling (`static/js/chat-widget.js`)
- Added `getCsrfToken()` method to extract CSRF token from cookies
- Updated all POST requests to include `X-CSRFToken` header:
  - `startSession()`
  - `sendMessage()`
  - `closeSession()`

### 2. Fixed URL Path Construction
- Changed from `/chat/start/${this.productId || ''}` to proper conditional:
  ```javascript
  const url = this.productId ? `/chat/start/${this.productId}/` : '/chat/start/';
  ```
- This prevents malformed URLs like `/chat/start/null`

### 3. Enhanced Error Handling
- Added response status checking
- Added detailed console logging for debugging
- Improved error messages for users
- Added server response text logging

### 4. Created Deployment Scripts
- **deploy_chat_fix.sh**: Automated deployment script
- **CHAT_TROUBLESHOOTING.md**: Comprehensive troubleshooting guide

## Deployment Steps

### Quick Deploy (Recommended)
```bash
# In PythonAnywhere Bash console
cd ~/monticlairs-wardrobe
bash deploy_chat_fix.sh
```

### Manual Deploy
```bash
cd ~/monticlairs-wardrobe
source venv/bin/activate
git pull origin main
python manage.py collectstatic --noinput
touch /var/www/chiz13_pythonanywhere_com_wsgi.py
```

## Testing Steps

### 1. Browser Console Test
1. Open your website: https://chiz13.pythonanywhere.com
2. Press F12 to open DevTools
3. Go to Console tab
4. Click the gold chat button
5. Try to send a message
6. Check console for any errors

### 2. Network Tab Test
1. Open DevTools (F12)
2. Go to Network tab
3. Click chat button
4. Look for these requests:
   - `/chat/start/` - Should return 200 with JSON
   - `/chat/send/<session_id>/` - Should return 200 with JSON
5. If you see 404/500 errors, check error logs

### 3. Manual API Test
```bash
# In PythonAnywhere console
curl -X POST https://chiz13.pythonanywhere.com/chat/start/ \
  -H "Content-Type: application/json" \
  -d '{"guest_name":"Test","guest_email":"test@test.com"}'
```

Expected response:
```json
{"success":true,"session_id":"...","created":true}
```

## Common Issues & Solutions

### Issue 1: 404 Not Found
**Cause**: Static files not collected
**Solution**: Run `python manage.py collectstatic --noinput`

### Issue 2: 403 Forbidden
**Cause**: CSRF token issue (should be fixed now)
**Solution**: Clear browser cache and cookies

### Issue 3: 500 Internal Server Error
**Cause**: Backend error (database, view logic)
**Solution**: Check error logs:
```bash
tail -n 100 /var/log/chiz13.pythonanywhere.com.error.log
```

### Issue 4: Chat button not appearing
**Cause**: JavaScript not loading
**Solution**: 
1. Check if `chat-widget.js` exists in staticfiles
2. Verify static files mapping in PythonAnywhere Web tab
3. Clear browser cache

### Issue 5: Database errors
**Cause**: Migrations not applied
**Solution**: Run `python manage.py migrate`

## Verification Checklist

After deployment, verify:

- [ ] Chat button appears on all pages (bottom-right, gold color)
- [ ] Clicking chat button opens chat window
- [ ] Guest form appears for non-logged-in users
- [ ] Can enter name and email
- [ ] Can send messages without errors
- [ ] Messages appear in chat window
- [ ] No errors in browser console
- [ ] No 404 errors in Network tab

## Files Modified

1. `static/js/chat-widget.js` - Added CSRF tokens, fixed URLs, enhanced error handling
2. `deploy_chat_fix.sh` - New deployment script
3. `CHAT_TROUBLESHOOTING.md` - New troubleshooting guide
4. `CHAT_FIX_SUMMARY.md` - This file

## Next Steps

1. **Commit changes to Git**:
   ```bash
   git add .
   git commit -m "Fix chat system CSRF and error handling"
   git push origin main
   ```

2. **Deploy to PythonAnywhere**:
   ```bash
   cd ~/monticlairs-wardrobe
   bash deploy_chat_fix.sh
   ```

3. **Test thoroughly**:
   - Test as guest user
   - Test as logged-in user
   - Test on different pages
   - Test sending multiple messages

4. **Monitor error logs**:
   ```bash
   tail -f /var/log/chiz13.pythonanywhere.com.error.log
   ```

## Support

If issues persist after following all steps:

1. Check browser console for JavaScript errors
2. Check Network tab for failed requests
3. Check PythonAnywhere error logs
4. Verify all files are in staticfiles directory
5. Ensure database migrations are applied
6. Verify ALLOWED_HOSTS includes 'chiz13.pythonanywhere.com'

## Technical Details

### CSRF Token Implementation
```javascript
getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
```

### Backend Views (Already Configured)
- All chat views have `@csrf_exempt` decorator
- Views return proper JSON responses
- Error handling in place

### URL Patterns (Already Configured)
```python
path('chat/start/', views.start_chat_session, name='start_chat_session'),
path('chat/start/<int:product_id>/', views.start_chat_session, name='start_chat_session_product'),
path('chat/send/<str:session_id>/', views.send_message, name='send_message'),
path('chat/messages/<str:session_id>/', views.get_messages, name='get_messages'),
path('chat/close/<str:session_id>/', views.close_chat, name='close_chat'),
```

## Conclusion

The chat system should now work correctly on PythonAnywhere. The main fixes were:
1. Adding CSRF tokens to all POST requests
2. Fixing URL path construction
3. Enhancing error handling and logging
4. Providing deployment and troubleshooting guides

Follow the deployment steps above and test thoroughly. If issues persist, use the troubleshooting guide to diagnose the problem.
