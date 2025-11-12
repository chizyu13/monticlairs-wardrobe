"""
Payment Integration Tests

Tests for payment processing, webhooks, and notifications.
Run with: python manage.py test payment
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail
from unittest.mock import patch, Mock
import json
import stripe

from .models import Payment


class PaymentModelTests(TestCase):
    """Tests for Payment model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_payment_creation(self):
        """Test creating a payment record."""
        payment = Payment.objects.create(
            user=self.user,
            method='stripe',
            amount=100.00,
            reference='TEST123',
            status='pending'
        )
        
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.amount, 100.00)
        self.assertEqual(payment.status, 'pending')
    
    def test_mark_as_completed(self):
        """Test marking payment as completed."""
        payment = Payment.objects.create(
            user=self.user,
            method='stripe',
            amount=100.00,
            reference='TEST123',
            status='pending'
        )
        
        payment.mark_as_completed()
        payment.refresh_from_db()
        
        self.assertEqual(payment.status, 'completed')
        self.assertIsNotNone(payment.completed_at)
    
    def test_mark_as_failed(self):
        """Test marking payment as failed."""
        payment = Payment.objects.create(
            user=self.user,
            method='stripe',
            amount=100.00,
            reference='TEST123',
            status='pending'
        )
        
        error_msg = 'Insufficient funds'
        payment.mark_as_failed(error_msg)
        payment.refresh_from_db()
        
        self.assertEqual(payment.status, 'failed')
        self.assertEqual(payment.error_message, error_msg)
    
    def test_can_retry(self):
        """Test retry logic."""
        payment = Payment.objects.create(
            user=self.user,
            method='stripe',
            amount=100.00,
            reference='TEST123',
            status='failed',
            retry_count=0
        )
        
        self.assertTrue(payment.can_retry())
        
        payment.retry_count = 3
        payment.save()
        
        self.assertFalse(payment.can_retry())


class StripeWebhookTests(TestCase):
    """Tests for Stripe webhook handling."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.payment = Payment.objects.create(
            user=self.user,
            method='stripe',
            amount=100.00,
            reference='TEST123',
            status='pending'
        )
    
    @patch('stripe.Webhook.construct_event')
    def test_stripe_payment_success_webhook(self, mock_construct):
        """Test Stripe payment success webhook."""
        # Mock webhook event
        mock_event = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test123',
                    'amount': 10000,  # 100.00 in cents
                    'metadata': {
                        'user_id': str(self.user.id)
                    }
                }
            }
        }
        mock_construct.return_value = mock_event
        
        # Send webhook request
        response = self.client.post(
            reverse('payment:stripe_webhook'),
            data=json.dumps(mock_event),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check payment was updated
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'completed')
    
    @patch('stripe.Webhook.construct_event')
    def test_stripe_payment_failure_webhook(self, mock_construct):
        """Test Stripe payment failure webhook."""
        mock_event = {
            'type': 'payment_intent.payment_failed',
            'data': {
                'object': {
                    'id': 'pi_test123',
                    'last_payment_error': {
                        'message': 'Card declined'
                    },
                    'metadata': {
                        'user_id': str(self.user.id)
                    }
                }
            }
        }
        mock_construct.return_value = mock_event
        
        response = self.client.post(
            reverse('payment:stripe_webhook'),
            data=json.dumps(mock_event),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check payment was marked as failed
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'failed')
        self.assertIn('Card declined', self.payment.error_message)


class MTNWebhookTests(TestCase):
    """Tests for MTN Mobile Money webhook handling."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.payment = Payment.objects.create(
            user=self.user,
            method='mtn',
            amount=100.00,
            reference='MTN_TEST123',
            status='pending'
        )
    
    def test_mtn_payment_success_webhook(self):
        """Test MTN payment success webhook."""
        webhook_data = {
            'financialTransactionId': 'mtn_trans_123',
            'externalId': 'MTN_TEST123',
            'status': 'SUCCESSFUL',
            'amount': '100.00',
            'currency': 'ZMW'
        }
        
        response = self.client.post(
            reverse('payment:mtn_webhook'),
            data=json.dumps(webhook_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check payment was updated
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'completed')
    
    def test_mtn_payment_failure_webhook(self):
        """Test MTN payment failure webhook."""
        webhook_data = {
            'financialTransactionId': 'mtn_trans_123',
            'externalId': 'MTN_TEST123',
            'status': 'FAILED',
            'reason': 'Insufficient balance'
        }
        
        response = self.client.post(
            reverse('payment:mtn_webhook'),
            data=json.dumps(webhook_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check payment was marked as failed
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'failed')


class AirtelWebhookTests(TestCase):
    """Tests for Airtel Money webhook handling."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.payment = Payment.objects.create(
            user=self.user,
            method='airtel',
            amount=100.00,
            reference='AIRTEL_TEST123',
            status='pending'
        )
    
    def test_airtel_payment_success_webhook(self):
        """Test Airtel payment success webhook."""
        webhook_data = {
            'transaction': {
                'id': 'airtel_trans_123',
                'status': 'SUCCESS',
                'reference': 'AIRTEL_TEST123',
                'amount': '100.00',
                'currency': 'ZMW'
            }
        }
        
        response = self.client.post(
            reverse('payment:airtel_webhook'),
            data=json.dumps(webhook_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check payment was updated
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'completed')
    
    def test_airtel_payment_failure_webhook(self):
        """Test Airtel payment failure webhook."""
        webhook_data = {
            'transaction': {
                'id': 'airtel_trans_123',
                'status': 'FAILED',
                'reference': 'AIRTEL_TEST123',
                'message': 'Transaction declined'
            }
        }
        
        response = self.client.post(
            reverse('payment:airtel_webhook'),
            data=json.dumps(webhook_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check payment was marked as failed
        self.payment.refresh_from_db()
        self.assertEqual(payment.status, 'failed')


class PaymentNotificationTests(TestCase):
    """Tests for payment email notifications."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.payment = Payment.objects.create(
            user=self.user,
            method='stripe',
            amount=100.00,
            reference='TEST123',
            status='pending'
        )
    
    def test_payment_confirmation_email(self):
        """Test payment confirmation email is sent."""
        from payment.views import send_payment_confirmation_email
        
        # Mark payment as completed
        self.payment.mark_as_completed()
        
        # Send confirmation email
        result = send_payment_confirmation_email(self.payment)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Payment Confirmation', mail.outbox[0].subject)
        self.assertIn(self.user.email, mail.outbox[0].to)
    
    def test_payment_failure_email(self):
        """Test payment failure email is sent."""
        from payment.views import send_payment_failure_email
        
        # Mark payment as failed
        self.payment.mark_as_failed('Card declined')
        
        # Send failure email
        result = send_payment_failure_email(self.payment)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Payment Failed', mail.outbox[0].subject)
        self.assertIn(self.user.email, mail.outbox[0].to)
    
    def test_payment_pending_email(self):
        """Test payment pending email is sent."""
        from payment.views import send_payment_pending_email
        
        # Send pending email
        result = send_payment_pending_email(self.payment)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Order Received', mail.outbox[0].subject)
        self.assertIn(self.user.email, mail.outbox[0].to)


class PaymentErrorHandlingTests(TestCase):
    """Tests for payment error handling."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    @patch('stripe.PaymentIntent.create')
    def test_stripe_card_declined_error(self, mock_create):
        """Test handling of Stripe card declined error."""
        mock_create.side_effect = stripe.error.CardError(
            message='Card declined',
            param='card',
            code='card_declined'
        )
        
        response = self.client.post(
            reverse('payment:create_payment_intent'),
            data=json.dumps({'amount': 10000, 'currency': 'zmw'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    @patch('stripe.PaymentIntent.create')
    def test_stripe_network_error(self, mock_create):
        """Test handling of Stripe network error."""
        mock_create.side_effect = stripe.error.APIConnectionError(
            message='Network error'
        )
        
        response = self.client.post(
            reverse('payment:create_payment_intent'),
            data=json.dumps({'amount': 10000, 'currency': 'zmw'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.content)
        self.assertIn('error', data)
