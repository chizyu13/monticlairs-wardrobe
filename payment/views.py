import logging
import stripe
import requests
import json
import time
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Payment
from django.core.exceptions import ImproperlyConfigured
from requests.exceptions import RequestException, Timeout, ConnectionError
from django.db import transaction

# Set up logging
logger = logging.getLogger(__name__)

# Payment error messages
PAYMENT_ERROR_MESSAGES = {
    'network_error': 'Network error occurred. Please check your connection and try again.',
    'timeout_error': 'Payment request timed out. Please try again.',
    'invalid_amount': 'Invalid payment amount. Please check and try again.',
    'insufficient_funds': 'Insufficient funds. Please check your account balance.',
    'payment_declined': 'Payment was declined. Please try a different payment method.',
    'api_error': 'Payment service is temporarily unavailable. Please try again later.',
    'invalid_credentials': 'Payment credentials are invalid. Please contact support.',
    'generic_error': 'An error occurred while processing your payment. Please try again.',
}

# Configure Stripe API key
if not hasattr(settings, 'STRIPE_SECRET_KEY'):
    logger.error("STRIPE_SECRET_KEY is not defined in settings")
    raise ImproperlyConfigured("STRIPE_SECRET_KEY is required")
stripe.api_key = settings.STRIPE_SECRET_KEY

# Helper functions for error handling
def handle_payment_error(payment, error_type, error_message, user_message=None):
    """
    Centralized error handling for payment failures.
    
    Args:
        payment: Payment instance
        error_type: Type of error (for logging)
        error_message: Detailed error message (for logging)
        user_message: User-friendly message (optional)
    """
    logger.error(f"Payment {payment.id} failed - {error_type}: {error_message}")
    
    payment.status = 'failed'
    payment.error_message = error_message[:500]  # Store first 500 chars
    payment.save()
    
    return user_message or PAYMENT_ERROR_MESSAGES.get(error_type, PAYMENT_ERROR_MESSAGES['generic_error'])

def retry_api_call(func, max_retries=3, timeout=10):
    """
    Retry an API call with exponential backoff.
    
    Args:
        func: Function to call
        max_retries: Maximum number of retry attempts
        timeout: Timeout in seconds for each attempt
    
    Returns:
        Response object or raises exception
    """
    for attempt in range(max_retries):
        try:
            response = func(timeout=timeout)
            return response
        except Timeout:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            logger.warning(f"API call timed out, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait_time)
        except ConnectionError:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            logger.warning(f"Connection error, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait_time)
    
    raise Exception("Max retries exceeded")

# Airtel Money API credentials (replace with actual values)
AIRTEL_API_URL = "https://api.airtel.com/airtel-money"
AIRTEL_CLIENT_ID = "your_airtel_client_id"
AIRTEL_CLIENT_SECRET = "your_airtel_client_secret"
AIRTEL_ACCESS_TOKEN_URL = "https://api.airtel.com/oauth/token"

# MTN API credentials (replace with actual values)
MTN_API_URL = "https://api.mtn.com/momo"
MTN_API_KEY = "your_mtn_api_key"

def checkout_view(request):
    """Render the checkout page."""
    cart_items = request.session.get('cart', [])
    total_price = sum(item['price'] for item in cart_items) if cart_items else 0.00

    logger.debug(f"Rendering checkout with total_price: {total_price}")
    context = {
        'total_price': f"{total_price:.2f}",
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'payment/checkout.html', context)

@csrf_exempt
@require_POST
def create_payment_intent(request):
    """Create a Stripe PaymentIntent with enhanced error handling."""
    logger.debug(f"Received payment intent request: {request.body}")
    
    try:
        data = json.loads(request.body)
        amount = data.get('amount')
        currency = data.get('currency', 'zmw')

        # Validate amount
        if not amount or amount <= 0:
            logger.error(f"Invalid amount received: {amount}")
            return JsonResponse({
                'error': PAYMENT_ERROR_MESSAGES['invalid_amount']
            }, status=400)

        # Create payment intent with retry logic
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                payment_method_types=['card'],
                metadata={
                    'user_id': request.user.id if request.user.is_authenticated else None,
                }
            )
            
            logger.info(f"Payment intent created: {intent.id}")
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
            
        except stripe.error.CardError as e:
            # Card was declined
            logger.error(f"Card declined: {str(e)}")
            return JsonResponse({
                'error': PAYMENT_ERROR_MESSAGES['payment_declined']
            }, status=400)
            
        except stripe.error.RateLimitError as e:
            # Too many requests
            logger.error(f"Stripe rate limit: {str(e)}")
            return JsonResponse({
                'error': 'Too many requests. Please try again in a moment.'
            }, status=429)
            
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters
            logger.error(f"Invalid Stripe request: {str(e)}")
            return JsonResponse({
                'error': PAYMENT_ERROR_MESSAGES['invalid_amount']
            }, status=400)
            
        except stripe.error.AuthenticationError as e:
            # Authentication failed
            logger.error(f"Stripe authentication error: {str(e)}")
            return JsonResponse({
                'error': PAYMENT_ERROR_MESSAGES['invalid_credentials']
            }, status=500)
            
        except stripe.error.APIConnectionError as e:
            # Network communication failed
            logger.error(f"Stripe connection error: {str(e)}")
            return JsonResponse({
                'error': PAYMENT_ERROR_MESSAGES['network_error']
            }, status=503)
            
        except stripe.error.StripeError as e:
            # Generic Stripe error
            logger.error(f"Stripe error: {str(e)}")
            return JsonResponse({
                'error': PAYMENT_ERROR_MESSAGES['api_error']
            }, status=500)
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({
            'error': 'Invalid request format'
        }, status=400)
        
    except Exception as e:
        logger.error(f"Unexpected error in create_payment_intent: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': PAYMENT_ERROR_MESSAGES['generic_error']
        }, status=500)

@login_required
@require_POST
def process_payment(request):
    """Handle all payment methods."""
    logger.debug(f"Processing payment request: {request.POST}")
    payment_method = request.POST.get('payment_method')
    amount = float(request.POST.get('total_price', 0))  # Total including delivery fee
    phone_number = request.POST.get('phone_number')
    location = request.POST.get('location')
    gps_location = request.POST.get('gps_location')
    hostel_name = request.POST.get('hostel_name', '')
    room_number = request.POST.get('room_number', '')

    if not payment_method:
        logger.error("No payment method selected")
        messages.error(request, "Please select a payment method.")
        return redirect('home:checkout')

    # Create a Payment record
    payment = Payment.objects.create(
        user=request.user,
        method=payment_method,
        amount=amount,
        reference=f"{payment_method.upper()}_{request.user.id}_{int(time.time())}",
        status='pending',
        phone_number=phone_number,
        location=location,
        gps_location=gps_location,
        hostel_name=hostel_name,
        room_number=room_number
    )

    if payment_method == 'stripe':
        # Handled client-side in checkout.html, but confirm server-side
        logger.info(f"Stripe payment initiated for payment ID: {payment.id}")
        return JsonResponse({'redirect_url': '/payments/success/'})  # Client handles Stripe

    elif payment_method == 'airtel':
        logger.debug(f"Processing Airtel payment for amount: {amount}")
        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': AIRTEL_CLIENT_ID,
            'client_secret': AIRTEL_CLIENT_SECRET
        }
        response = requests.post(AIRTEL_ACCESS_TOKEN_URL, data=auth_data)

        if response.status_code != 200:
            logger.error(f"Failed to get Airtel access token: {response.text}")
            messages.error(request, "Failed to initiate Airtel payment.")
            payment.status = 'failed'
            payment.save()
            return redirect('payment:airtel_payment_fail')

        access_token = response.json().get('access_token')
        if not access_token:
            logger.error("No access token received from Airtel")
            messages.error(request, "Airtel payment initialization failed.")
            payment.status = 'failed'
            payment.save()
            return redirect('payment:airtel_payment_fail')

        payment_data = {
            'amount': amount,
            'currency': 'ZMW',
            'callback_url': request.build_absolute_uri('/payment/airtel-payment-success/'),
            'failure_url': request.build_absolute_uri('/payment/airtel-payment-fail/'),
        }
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        response = requests.post(f"{AIRTEL_API_URL}/payments/initiate", json=payment_data, headers=headers)

        if response.status_code == 200:
            logger.info(f"Airtel payment initiated: {response.json()}")
            payment_link = response.json().get('payment_link')
            payment.reference = response.json().get('reference', payment.reference)
            payment.save()
            return redirect(payment_link)
        else:
            logger.error(f"Airtel payment failed: {response.text}")
            messages.error(request, "Airtel payment failed.")
            payment.status = 'failed'
            payment.save()
            return redirect('payment:airtel_payment_fail')

    elif payment_method == 'mtn':
        logger.debug(f"Processing MTN payment for amount: {amount}")
        payment_data = {
            'amount': amount,
            'currency': 'ZMW',
            'externalId': payment.reference,
            'payer': {
                'partyIdType': 'MSISDN',
                'partyId': phone_number
            },
            'payerMessage': 'Payment for Montclair Wardrobe',
            'payeeNote': 'Montclair Wardrobe Order'
        }
        headers = {
            'Authorization': f'Bearer {MTN_API_KEY}',
            'Content-Type': 'application/json',
            'X-Target-Environment': 'sandbox',
        }
        response = requests.post(f"{MTN_API_URL}/collection/v1_0/requesttopay", json=payment_data, headers=headers)

        if response.status_code == 202:
            logger.info(f"MTN payment initiated: {response.json()}")
            payment.reference = response.json().get('transactionId', payment.reference)
            payment.status = 'pending'
            payment.save()
            return redirect('payment:mtn_payment_success')
        else:
            logger.error(f"MTN payment failed: {response.text}")
            messages.error(request, "MTN payment failed.")
            payment.status = 'failed'
            payment.save()
            return redirect('payment:mtn_payment_fail')

    elif payment_method in ('cash', 'delivery'):
        logger.info(f"{payment_method.capitalize()} payment recorded for payment ID: {payment.id}")
        payment.status = 'pending'  # Will be confirmed on delivery
        payment.save()
        messages.success(request, f"{payment_method.capitalize()} payment recorded. Please prepare the amount for delivery.")
        return redirect('payment:payment_success')

    else:
        logger.error(f"Invalid payment method: {payment_method}")
        messages.error(request, "Invalid payment method.")
        payment.status = 'failed'
        payment.save()
        return redirect('payment:checkout')

@login_required
def airtel_payment(request):
    """Render Airtel payment page (optional)."""
    logger.debug("Rendering Airtel payment page")
    return render(request, 'payment/airtel.html')

def airtel_payment_success(request):
    """Handle Airtel payment success."""
    logger.debug(f"Airtel payment success callback: {request.GET}")
    reference = request.GET.get('reference')
    if reference:
        Payment.objects.filter(reference=reference).update(status='completed')
        messages.success(request, "Airtel payment completed successfully.")
    return render(request, 'payment/airtel_payment_success.html')

def airtel_payment_fail(request):
    """Handle Airtel payment failure."""
    logger.debug(f"Airtel payment failure callback: {request.GET}")
    messages.error(request, "Airtel payment failed.")
    return render(request, 'payment/airtel_payment_fail.html')

@login_required
def mtn_payment(request):
    """Render MTN payment page (optional)."""
    logger.debug("Rendering MTN payment page")
    return render(request, 'payment/mtn.html')

def mtn_payment_success(request):
    """Handle MTN payment success."""
    logger.debug(f"MTN payment success callback: {request.GET}")
    reference = request.GET.get('transactionId')
    if reference:
        Payment.objects.filter(reference=reference).update(status='completed')
        messages.success(request, "MTN payment completed successfully.")
    return render(request, 'payment/mtn_payment_success.html')

def mtn_payment_fail(request):
    """Handle MTN payment failure."""
    logger.debug(f"MTN payment failure callback: {request.GET}")
    messages.error(request, "MTN payment failed.")
    return render(request, 'payment/mtn_payment_fail.html')

def payment_success(request):
    """Render generic payment success page."""
    logger.debug("Rendering payment success page")
    return render(request, 'payment/success.html')

def payment_cancel(request):
    """Render generic payment cancel page."""
    logger.debug("Rendering payment cancel page")
    return render(request, 'payment/cancel.html')


# ===========================
# Webhook Handlers
# ===========================

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhook events for payment confirmation.
    Verifies webhook signature for security.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    # Get webhook secret from settings
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
    
    if not webhook_secret:
        logger.error("STRIPE_WEBHOOK_SECRET not configured")
        return JsonResponse({'error': 'Webhook not configured'}, status=500)
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        logger.info(f"Stripe webhook received: {event['type']}")
        
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid Stripe webhook payload: {str(e)}")
        return JsonResponse({'error': 'Invalid payload'}, status=400)
        
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid Stripe webhook signature: {str(e)}")
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_stripe_payment_success(payment_intent)
        
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_stripe_payment_failure(payment_intent)
        
    elif event['type'] == 'charge.refunded':
        charge = event['data']['object']
        handle_stripe_refund(charge)
        
    else:
        logger.info(f"Unhandled Stripe event type: {event['type']}")
    
    return JsonResponse({'status': 'success'})


def handle_stripe_payment_success(payment_intent):
    """Handle successful Stripe payment."""
    try:
        payment_intent_id = payment_intent['id']
        amount = payment_intent['amount'] / 100  # Convert from cents
        
        # Find payment by reference or metadata
        metadata = payment_intent.get('metadata', {})
        user_id = metadata.get('user_id')
        
        if user_id:
            # Update payment status
            payment = Payment.objects.filter(
                user_id=user_id,
                amount=amount,
                status='pending'
            ).first()
            
            if payment:
                payment.mark_as_completed()
                payment.reference = payment_intent_id
                payment.save()
                logger.info(f"Payment {payment.id} marked as completed via Stripe webhook")
                
                # Send confirmation email
                send_payment_confirmation_email(payment)
            else:
                logger.warning(f"No matching payment found for Stripe payment intent {payment_intent_id}")
        else:
            logger.warning(f"No user_id in Stripe payment intent metadata: {payment_intent_id}")
            
    except Exception as e:
        logger.error(f"Error handling Stripe payment success: {str(e)}", exc_info=True)


def handle_stripe_payment_failure(payment_intent):
    """Handle failed Stripe payment."""
    try:
        payment_intent_id = payment_intent['id']
        error_message = payment_intent.get('last_payment_error', {}).get('message', 'Payment failed')
        
        metadata = payment_intent.get('metadata', {})
        user_id = metadata.get('user_id')
        
        if user_id:
            payment = Payment.objects.filter(
                user_id=user_id,
                status='pending'
            ).first()
            
            if payment:
                payment.mark_as_failed(error_message)
                logger.info(f"Payment {payment.id} marked as failed via Stripe webhook")
                
                # Send failure notification email
                send_payment_failure_email(payment)
            else:
                logger.warning(f"No matching payment found for failed Stripe payment {payment_intent_id}")
                
    except Exception as e:
        logger.error(f"Error handling Stripe payment failure: {str(e)}", exc_info=True)


def handle_stripe_refund(charge):
    """Handle Stripe refund."""
    try:
        charge_id = charge['id']
        refund_amount = charge['amount_refunded'] / 100
        
        logger.info(f"Stripe refund processed for charge {charge_id}: {refund_amount}")
        # Add refund handling logic here
        
    except Exception as e:
        logger.error(f"Error handling Stripe refund: {str(e)}", exc_info=True)


@csrf_exempt
@require_POST
def mtn_webhook(request):
    """
    Handle MTN Mobile Money webhook for payment confirmation.
    """
    try:
        # Parse webhook data
        data = json.loads(request.body)
        logger.info(f"MTN webhook received: {data}")
        
        # Extract payment details
        transaction_id = data.get('financialTransactionId')
        status = data.get('status')
        external_id = data.get('externalId')  # Our payment reference
        
        if not transaction_id or not external_id:
            logger.error("Missing required fields in MTN webhook")
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Find payment by reference
        try:
            payment = Payment.objects.get(reference=external_id)
            
            if status == 'SUCCESSFUL':
                payment.mark_as_completed()
                logger.info(f"MTN payment {payment.id} marked as completed")
                
            elif status == 'FAILED':
                error_message = data.get('reason', 'Payment failed')
                payment.mark_as_failed(error_message)
                logger.info(f"MTN payment {payment.id} marked as failed: {error_message}")
                
            else:
                logger.warning(f"Unknown MTN payment status: {status}")
                
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for MTN reference: {external_id}")
            return JsonResponse({'error': 'Payment not found'}, status=404)
        
        return JsonResponse({'status': 'success'})
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in MTN webhook")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
    except Exception as e:
        logger.error(f"Error handling MTN webhook: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_POST
def airtel_webhook(request):
    """
    Handle Airtel Money webhook for payment confirmation.
    """
    try:
        # Parse webhook data
        data = json.loads(request.body)
        logger.info(f"Airtel webhook received: {data}")
        
        # Extract payment details
        transaction_id = data.get('transaction', {}).get('id')
        status = data.get('transaction', {}).get('status')
        reference = data.get('transaction', {}).get('reference')  # Our payment reference
        
        if not transaction_id or not reference:
            logger.error("Missing required fields in Airtel webhook")
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Verify webhook signature if provided
        signature = request.META.get('HTTP_X_AIRTEL_SIGNATURE')
        if signature:
            # Add signature verification logic here
            pass
        
        # Find payment by reference
        try:
            payment = Payment.objects.get(reference=reference)
            
            if status in ['SUCCESS', 'SUCCESSFUL']:
                payment.mark_as_completed()
                logger.info(f"Airtel payment {payment.id} marked as completed")
                
            elif status in ['FAILED', 'DECLINED']:
                error_message = data.get('transaction', {}).get('message', 'Payment failed')
                payment.mark_as_failed(error_message)
                logger.info(f"Airtel payment {payment.id} marked as failed: {error_message}")
                
            else:
                logger.warning(f"Unknown Airtel payment status: {status}")
                
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for Airtel reference: {reference}")
            return JsonResponse({'error': 'Payment not found'}, status=404)
        
        return JsonResponse({'status': 'success'})
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Airtel webhook")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
    except Exception as e:
        logger.error(f"Error handling Airtel webhook: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


# ===========================
# Payment Notification Functions
# ===========================

def send_payment_confirmation_email(payment):
    """
    Send email confirmation when payment is completed.
    
    Args:
        payment: Payment instance
    """
    try:
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        
        user = payment.user
        
        # Prepare email context
        context = {
            'user': user,
            'payment': payment,
            'amount': payment.amount,
            'reference': payment.reference,
            'method': payment.get_method_display(),
            'date': payment.completed_at or payment.created_at,
        }
        
        # Render email template
        html_message = render_to_string('payment/emails/payment_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=f'Payment Confirmation - Order #{payment.reference}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Payment confirmation email sent to {user.email} for payment {payment.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send payment confirmation email for payment {payment.id}: {str(e)}", exc_info=True)
        return False


def send_payment_failure_email(payment):
    """
    Send email notification when payment fails.
    
    Args:
        payment: Payment instance
    """
    try:
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        
        user = payment.user
        
        # Prepare email context
        context = {
            'user': user,
            'payment': payment,
            'amount': payment.amount,
            'reference': payment.reference,
            'method': payment.get_method_display(),
            'error_message': payment.error_message or 'Payment could not be processed',
            'can_retry': payment.can_retry(),
        }
        
        # Render email template
        html_message = render_to_string('payment/emails/payment_failure.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=f'Payment Failed - Order #{payment.reference}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Payment failure email sent to {user.email} for payment {payment.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send payment failure email for payment {payment.id}: {str(e)}", exc_info=True)
        return False


def send_payment_pending_email(payment):
    """
    Send email notification for pending payments (e.g., cash on delivery).
    
    Args:
        payment: Payment instance
    """
    try:
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        
        user = payment.user
        
        # Prepare email context
        context = {
            'user': user,
            'payment': payment,
            'amount': payment.amount,
            'reference': payment.reference,
            'method': payment.get_method_display(),
            'location': payment.location,
            'phone_number': payment.phone_number,
        }
        
        # Render email template
        html_message = render_to_string('payment/emails/payment_pending.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=f'Order Received - #{payment.reference}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Payment pending email sent to {user.email} for payment {payment.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send payment pending email for payment {payment.id}: {str(e)}", exc_info=True)
        return False
