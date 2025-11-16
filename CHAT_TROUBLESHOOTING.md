# Live Chat Troubleshooting Guide for PythonAnywhere

## Issue: "Failed to send message. Please try again."

This error occurs when the chat widget cannot communicate with the backend. Here are the solutions:

---

## Solution 1: Collect Static Files (MOST COMMON)

The chat widget JavaScript and CSS files need to be collected to the static files directory.

### Steps:
```bash
# SSH into PythonAnywhere console
cd ~/monticlairs-wardrobe

# Activate virtual environment
source venv/bin/activate

# Collect static files
python manage.py collectstatic --noinput

# Reload web app
touch /var/www/chiz13_pythonanywhere_com_wsgi.py
```

---

## Solution 2: Check Database Migrations

Ensure the ChatSession and ChatMessage models are migrated.

### Steps:
```bash
cd ~/monticlairs-wardrobe
source venv/bin/activate

# Check migrations
python manage.py showmigrations home

# If not migrated, run:
python manage.py migrate

# Reload web app
touch /var/www/chiz13_pythonanywhere_com_wsgi.py
```

---

## Solution 3: Verify URL Configuration

Check that chat URLs are properly configured.

### Test in PythonAnywhere console:
```bash
cd ~/monticlairs-wardrobe
source venv/bin/activate
python manage.py shell
```

Then in the Python shell:
```python
from django.urls import reverse
print(reverse('home:start_chat_session'))
# Should print: /chat/start/
```

---

## Solution 4: Check Error Logs

View the error logs to see what's failing:

```bash
# View last 100 lines of error log
tail -n 100 /var/log/chiz13.pythonanywhere.com.error.log

# Or view server log
tail -n 100 /var/log/chiz13.pythonanywhere.com.server.log
```

Common errors:
- **ImportError**: Missing dependencies
- **OperationalError**: Database not migrated
- **404 Error**: URLs not configured
- **500 Error**: View logic error

---

## Solution 5: Test Chat Endpoints Manually

Test if the backend is responding:

### Using curl (in PythonAnywhere console):
```bash
# Test start chat endpoint
curl -X POST https://chiz13.pythonanywhere.com/chat/start/ \
  -H "Content-Type: application/json" \
  -d '{"guest_name":"Test User","guest_email":"test@example.com"}'

# Should return: {"success":true,"session_id":"...","created":true}
```

### Using browser console (on your website):
```javascript
// Open browser DevTools (F12) and run:
fetch('/chat/start/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        guest_name: 'Test User',
        guest_email: 'test@example.com'
    })
})
.then(r => r.json())
.then(console.log)
.catch(console.error);
```

---

## Solution 6: Check ALLOWED_HOSTS

Ensure PythonAnywhere domain is in ALLOWED_HOSTS.

### In settings.py:
```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'chiz13.pythonanywhere.com',  # Add this
]
```

---

## Solution 7: Verify Static Files Configuration

### Check settings.py:
```python
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
```

### Check PythonAnywhere Web tab:
- Go to **Web** tab
- Scroll to **Static files** section
- Ensure mapping exists:
  - URL: `/static/`
  - Directory: `/home/chiz13/monticlairs-wardrobe/staticfiles`

---

## Solution 8: Browser Console Debugging

1. Open your website in browser
2. Press **F12** to open DevTools
3. Go to **Console** tab
4. Click the chat button
5. Look for errors:
   - **404 errors**: URLs not configured
   - **403 errors**: CSRF issue (should be fixed now)
   - **500 errors**: Backend error (check logs)
   - **Network errors**: Static files not loaded

---

## Solution 9: Check JavaScript Loading

### In browser DevTools:
1. Go to **Network** tab
2. Refresh page
3. Look for `chat-widget.js` and `chat-widget.css`
4. If they show **404**, static files aren't collected
5. If they show **200**, files are loading correctly

---

## Solution 10: Database Connection

Ensure MySQL connection is working:

```bash
cd ~/monticlairs-wardrobe
source venv/bin/activate
python manage.py dbshell
```

If this fails, check database credentials in settings.py:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'chiz13$default',
        'USER': 'chiz13',
        'PASSWORD': 'muna130820',  # Verify this
        'HOST': 'chiz13.mysql.pythonanywhere-services.com',
    }
}
```

---

## Quick Fix Checklist

Run these commands in order:

```bash
# 1. Navigate to project
cd ~/monticlairs-wardrobe

# 2. Activate virtual environment
source venv/bin/activate

# 3. Pull latest code
git pull origin main

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run migrations
python manage.py migrate

# 6. Collect static files
python manage.py collectstatic --noinput

# 7. Check for errors
python manage.py check

# 8. Reload web app
touch /var/www/chiz13_pythonanywhere_com_wsgi.py

# 9. Check error log
tail -n 50 /var/log/chiz13.pythonanywhere.com.error.log
```

---

## Still Not Working?

### Check these files exist:
```bash
ls -la ~/monticlairs-wardrobe/static/js/chat-widget.js
ls -la ~/monticlairs-wardrobe/static/css/chat-widget.css
ls -la ~/monticlairs-wardrobe/staticfiles/js/chat-widget.js
ls -la ~/monticlairs-wardrobe/staticfiles/css/chat-widget.css
```

### Verify chat models exist:
```bash
python manage.py shell
```
```python
from home.models import ChatSession, ChatMessage
print(ChatSession.objects.count())
print(ChatMessage.objects.count())
```

---

## Contact Support

If none of these solutions work, provide:
1. Error log output
2. Browser console errors
3. Network tab screenshot
4. Output of `python manage.py check`
