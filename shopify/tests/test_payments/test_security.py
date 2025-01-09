from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from decimal import Decimal
import json

from ...models import ShopifyOrder, PaymentAttempt
from ...services.payment_gateway import PaymentGateway

class PaymentSecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass123'
        )
        self.order = ShopifyOrder.objects.create(
            order_reference='TEST123',
            amount=Decimal('100.00'),
            currency='USD',
            customer_email='test@example.com',
            customer_name='Test User',
            order_data={'line_items': []}
        )

    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access payment endpoints"""
        urls = [
            reverse('api:create-payment-intent', args=[self.order.id]),
            reverse('api:confirm-payment', args=[self.order.id]),
            reverse('api:refund-payment', args=[self.order.id]),
        ]

        for url in urls:
            response = self.client.post(url)
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f"Unauthorized access should be denied for {url}"
            )

    def test_csrf_protection(self):
        """Test CSRF protection on payment endpoints"""
        client = Client(enforce_csrf_checks=True)
        
        # Try to make request without CSRF token
        response = client.post(
            reverse('api:create-payment-intent', args=[self.order.id]),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_payment_amount_tampering(self):
        """Test protection against payment amount tampering"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Try to create payment with amount greater than order amount
        payment_data = {
            'amount': '150.00',  # Original amount is 100.00
            'payment_method': 'card'
        }
        
        response = self.client.post(
            reverse('api:create-payment', args=[self.order.id]),
            payment_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sql_injection_protection(self):
        """Test protection against SQL injection attempts"""
        malicious_reference = "TEST123' OR '1'='1"
        
        response = self.client.get(
            reverse('api:order-detail', args=[malicious_reference])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_payment_replay_attack(self):
        """Test protection against payment replay attacks"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Create a completed payment
        payment = PaymentAttempt.objects.create(
            order=self.order,
            amount=self.order.amount,
            status='COMPLETED',
            payment_method='card',
            payment_id='pi_123456'
        )

        # Try to confirm the same payment again
        response = self.client.post(
            reverse('api:confirm-payment', args=[self.order.id]),
            {'payment_intent_id': 'pi_123456'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('shopify.services.payment_gateway.PaymentGateway.create_payment_intent')
    def test_xss_protection(self, mock_create):
        """Test protection against XSS attacks"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Try to inject malicious script
        malicious_data = {
            'customer_name': '<script>alert("xss")</script>',
            'notes': '<img src="x" onerror="alert(\'xss\')">'
        }
        
        response = self.client.post(
            reverse('api:update-order', args=[self.order.id]),
            malicious_data
        )
        
        self.order.refresh_from_db()
        self.assertNotIn('<script>', self.order.customer_name)
        self.assertNotIn('<img', str(self.order.order_data.get('notes', '')))

    def test_rate_limiting(self):
        """Test rate limiting on payment endpoints"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Make multiple rapid requests
        for _ in range(10):
            response = self.client.post(
                reverse('api:create-payment-intent', args=[self.order.id])
            )
        
        # The last request should be rate limited
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_payment_method_validation(self):
        """Test validation of payment methods"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Try to use invalid payment method
        response = self.client.post(
            reverse('api:create-payment', args=[self.order.id]),
            {
                'amount': '100.00',
                'payment_method': 'invalid_method'  # Invalid payment method
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sensitive_data_exposure(self):
        """Test protection of sensitive payment data"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Create a payment
        payment = PaymentAttempt.objects.create(
            order=self.order,
            amount=self.order.amount,
            status='COMPLETED',
            payment_method='card',
            payment_id='pi_123456',
            metadata={'card_number': '4242424242424242'}
        )
        
        # Verify sensitive data is not exposed in API response
        response = self.client.get(
            reverse('api:payment-detail', args=[payment.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('4242424242424242', json.dumps(response.data))

    def test_permission_escalation(self):
        """Test prevention of permission escalation attempts"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Try to access admin-only endpoint
        response = self.client.post(
            reverse('api:refund-payment', args=[self.order.id]),
            {'amount': '100.00'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_idempotency(self):
        """Test idempotency of payment operations"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Make same request with same idempotency key
        headers = {'X-Idempotency-Key': 'test_key_123'}
        
        # First request
        response1 = self.client.post(
            reverse('api:create-payment-intent', args=[self.order.id]),
            HTTP_X_IDEMPOTENCY_KEY=headers['X-Idempotency-Key']
        )
        
        # Second request with same key
        response2 = self.client.post(
            reverse('api:create-payment-intent', args=[self.order.id]),
            HTTP_X_IDEMPOTENCY_KEY=headers['X-Idempotency-Key']
        )
        
        # Should return same response
        self.assertEqual(response1.data, response2.data) 