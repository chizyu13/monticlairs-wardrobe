# Payment Webhook Setup Guide

This guide explains how to configure webhooks for Stripe, MTN Mobile Money, and Airtel Money payment providers.

## Overview

Webhooks allow payment providers to notify your application about payment events (success, failure, refunds) asynchronously. This ensures reliable payment confirmation even if the user closes their browser.

## Webhook Endpoints

Your application exposes the following webhook endpoints:

- **Stripe**: `https://yourdomain.com/payment/webhooks/stripe/`
- **MTN Mobile Money**: `https://yourdomain.com/payment/webhooks/mtn/`
- **Airtel Money**: `https://yourdomain.com/payment/webhooks/airtel/`

## Stripe Webhook Setup

### 1. Get Your Webhook Secret

1. Log in to your [Stripe Dashboard](https://dashboard.stripe.com/)
2. Go to **Developers** → **Webhooks**
3. Click **Add endpoint**
4. Enter your webhook URL: `https://yourdomain.com/payment/webhooks/stripe/`
5. Select events to listen for:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.refunded`
6. Click **Add endpoint**
7. Copy the **Signing secret** (starts with `whsec_`)

### 2. Configure in Django Settings

Add to your `settings.py`:

```python
# Stripe Configuration
STRIPE_SECRET_KEY = 'sk_test_...'  # Your Stripe secret key
STRIPE_PUBLISHABLE_KEY = 'pk_test_...'  # Your Stripe publishable key
STRIPE_WEBHOOK_SECRET = 'whsec_...'  # Your webhook signing secret
```

### 3. Test Webhook

Use Stripe CLI to test locally:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/payment/webhooks/stripe/

# Trigger test events
stripe trigger payment_intent.succeeded
```

## MTN Mobile Money Webhook Setup

### 1. Register Webhook URL

1. Log in to your [MTN Developer Portal](https://momodeveloper.mtn.com/)
2. Go to your application settings
3. Add webhook URL: `https://yourdomain.com/payment/webhooks/mtn/`
4. Save the configuration

### 2. Configure in Django Settings

Add to your `settings.py`:

```python
# MTN Mobile Money Configuration
MTN_API_KEY = 'your_mtn_api_key'
MTN_API_USER = 'your_mtn_api_user'
MTN_SUBSCRIPTION_KEY = 'your_mtn_subscription_key'
MTN_CALLBACK_URL = 'https://yourdomain.com/payment/webhooks/mtn/'
```

### 3. Webhook Payload Format

MTN sends webhooks in this format:

```json
{
  "financialTransactionId": "123456789",
  "externalId": "your_payment_reference",
  "status": "SUCCESSFUL",
  "amount": "100.00",
  "currency": "ZMW",
  "reason": ""
}
```

## Airtel Money Webhook Setup

### 1. Register Webhook URL

1. Log in to your [Airtel Money Developer Portal](https://developers.airtel.africa/)
2. Navigate to your application
3. Add webhook URL: `https://yourdomain.com/payment/webhooks/airtel/`
4. Configure webhook signature verification (optional but recommended)

### 2. Configure in Django Settings

Add to your `settings.py`:

```python
# Airtel Money Configuration
AIRTEL_CLIENT_ID = 'your_airtel_client_id'
AIRTEL_CLIENT_SECRET = 'your_airtel_client_secret'
AIRTEL_API_URL = 'https://api.airtel.com/airtel-money'
AIRTEL_CALLBACK_URL = 'https://yourdomain.com/payment/webhooks/airtel/'
```

### 3. Webhook Payload Format

Airtel sends webhooks in this format:

```json
{
  "transaction": {
    "id": "AP123456789",
    "status": "SUCCESS",
    "reference": "your_payment_reference",
    "amount": "100.00",
    "currency": "ZMW",
    "message": "Payment successful"
  }
}
```

## Security Best Practices

### 1. Verify Webhook Signatures

Always verify webhook signatures to ensure requests are from legitimate sources:

- **Stripe**: Uses `Stripe-Signature` header (automatically verified in code)
- **MTN**: Implement HMAC signature verification
- **Airtel**: Check `X-Airtel-Signature` header

### 2. Use HTTPS

Always use HTTPS for webhook endpoints in production:

```python
# settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 3. Implement Idempotency

Webhooks may be sent multiple times. Ensure your handlers are idempotent:

```python
# Check if payment is already processed
if payment.status == 'completed':
    logger.info(f"Payment {payment.id} already completed, skipping")
    return
```

### 4. Log All Webhook Events

All webhook events are logged for debugging:

```python
# View logs
tail -f logs/payment_webhooks.log
```

## Testing Webhooks Locally

### Using ngrok

1. Install ngrok: `brew install ngrok`
2. Start your Django server: `python manage.py runserver`
3. Create tunnel: `ngrok http 8000`
4. Use the ngrok URL for webhook configuration: `https://abc123.ngrok.io/payment/webhooks/stripe/`

### Using Stripe CLI

```bash
# Forward webhooks to local server
stripe listen --forward-to localhost:8000/payment/webhooks/stripe/

# In another terminal, trigger test events
stripe trigger payment_intent.succeeded
stripe trigger payment_intent.payment_failed
```

## Monitoring Webhooks

### Check Webhook Status

View webhook delivery status in provider dashboards:

- **Stripe**: Dashboard → Developers → Webhooks → Click endpoint → View attempts
- **MTN**: Developer Portal → Webhooks → Delivery logs
- **Airtel**: Developer Portal → Webhooks → Event history

### Django Admin

View payment status in Django admin:

1. Go to `/admin/payment/payment/`
2. Filter by status: `pending`, `completed`, `failed`
3. Check `error_message` field for failed payments

## Troubleshooting

### Webhook Not Received

1. Check webhook URL is publicly accessible
2. Verify HTTPS is enabled
3. Check firewall/security group settings
4. Review provider dashboard for delivery errors

### Signature Verification Failed

1. Verify webhook secret is correct in settings
2. Check request headers are being passed correctly
3. Ensure no middleware is modifying request body

### Payment Not Updated

1. Check Django logs: `tail -f logs/django.log`
2. Verify payment reference matches
3. Check database for payment record
4. Review webhook payload format

## Support

For issues with:
- **Stripe**: https://support.stripe.com/
- **MTN**: https://momodeveloper.mtn.com/support
- **Airtel**: https://developers.airtel.africa/support

For application issues, check Django logs or contact your development team.
