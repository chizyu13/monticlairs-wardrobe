from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    # Checkout and payment processing
    path('checkout/', views.checkout_view, name='checkout'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    
    # Airtel Money
    path('airtel-payment/', views.airtel_payment, name='airtel_payment'),
    path('airtel-payment-success/', views.airtel_payment_success, name='airtel_payment_success'),
    path('airtel-payment-fail/', views.airtel_payment_fail, name='airtel_payment_fail'),
    
    # MTN Mobile Money
    path('mtn-payment/', views.mtn_payment, name='mtn_payment'),
    path('mtn-payment-success/', views.mtn_payment_success, name='mtn_payment_success'),
    path('mtn-payment-fail/', views.mtn_payment_fail, name='mtn_payment_fail'),
    
    # Generic success/cancel
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    
    # Webhook endpoints (CSRF exempt)
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('webhooks/mtn/', views.mtn_webhook, name='mtn_webhook'),
    path('webhooks/airtel/', views.airtel_webhook, name='airtel_webhook'),
]