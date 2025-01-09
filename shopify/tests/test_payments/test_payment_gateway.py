from django.test import TestCase
from unittest.mock import patch, MagicMock
from decimal import Decimal
from ...models import ShopifyOrder
from ...services.payment_gateway import PaymentGateway, PaymentError

class PaymentGatewayTests(TestCase):
    def setUp(self):
        self.order = ShopifyOrder.objects.create(
            order_reference='TEST123',
            amount=Decimal('100.00'),
            currency='USD',
            customer_email='test@example.com',
            customer_name='Test User',
            order_data={'line_items': []}
        )
        self.gateway = PaymentGateway()

    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_success(self, mock_create):
        # Mock successful payment intent creation
        mock_create.return_value = MagicMock(
            client_secret='secret_123',
            id='pi_123456'
        )

        result = self.gateway.create_payment_intent(self.order)
        
        self.assertEqual(result['client_secret'], 'secret_123')
        self.assertEqual(result['payment_intent_id'], 'pi_123456')
        mock_create.assert_called_once_with(
            amount=10000,  # 100.00 converted to cents
            currency='usd',
            metadata={'order_reference': 'TEST123'}
        )

    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_failure(self, mock_create):
        # Mock Stripe error
        mock_create.side_effect = PaymentError('Invalid currency')

        with self.assertRaises(PaymentError):
            self.gateway.create_payment_intent(self.order)

    @patch('stripe.PaymentIntent.retrieve')
    def test_confirm_payment_success(self, mock_retrieve):
        # Mock successful payment confirmation
        mock_retrieve.return_value = MagicMock(status='succeeded')
        
        result = self.gateway.confirm_payment('pi_123456')
        self.assertTrue(result)
        mock_retrieve.assert_called_once_with('pi_123456')

    @patch('stripe.PaymentIntent.retrieve')
    def test_confirm_payment_failure(self, mock_retrieve):
        # Mock failed payment
        mock_retrieve.return_value = MagicMock(status='failed')
        
        result = self.gateway.confirm_payment('pi_123456')
        self.assertFalse(result) 