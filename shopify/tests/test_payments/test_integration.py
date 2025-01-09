from django.test import TestCase, Client
from django.urls import reverse
from shopify.models import ShopifyOrder, PaymentAttempt
from decimal import Decimal
import json
from unittest.mock import patch

class PaymentIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.order = ShopifyOrder.objects.create(
            order_reference='TEST-001',
            amount=Decimal('100.00'),
            currency='USD',
            customer_email='test@example.com',
            customer_name='Test Customer'
        )

    @patch('shopify.services.payment_gateway.StripeGateway.create_payment_intent')
    @patch('shopify.services.payment_gateway.StripeGateway.confirm_payment')
    def test_complete_payment_flow(self, mock_confirm, mock_create_intent):
        # Step 1: Create payment intent
        mock_create_intent.return_value = {
            'success': True,
            'payment_intent_id': 'pi_123456',
            'client_secret': 'secret_123'
        }

        create_response = self.client.post(
            reverse('shopify:create_payment_intent'),
            data=json.dumps({'order_id': self.order.id}),
            content_type='application/json'
        )

        self.assertEqual(create_response.status_code, 200)
        
        # Step 2: Confirm payment
        mock_confirm.return_value = {
            'success': True,
            'status': 'succeeded',
            'amount': 100.00,
            'currency': 'usd'
        }

        confirm_response = self.client.post(
            reverse('shopify:confirm_payment'),
            data=json.dumps({'payment_intent_id': 'pi_123456'}),
            content_type='application/json'
        )

        self.assertEqual(confirm_response.status_code, 200)

        # Step 3: Verify final states
        self.order.refresh_from_db()
        payment = PaymentAttempt.objects.get(order=self.order)

        self.assertEqual(self.order.status, 'PAID')
        self.assertEqual(payment.status, 'SUCCEEDED')
        self.assertEqual(payment.transaction_id, 'pi_123456') 