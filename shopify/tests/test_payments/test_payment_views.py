from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from decimal import Decimal
from ...models import ShopifyOrder, PaymentAttempt
from ...services.payment_gateway import PaymentError

class PaymentViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.order = ShopifyOrder.objects.create(
            order_reference='TEST123',
            amount=Decimal('100.00'),
            currency='USD',
            customer_email='test@example.com',
            customer_name='Test User',
            order_data={'line_items': []}
        )
        self.payment_intent_url = reverse('api:create-payment-intent', args=[self.order.id])
        self.confirm_payment_url = reverse('api:confirm-payment', args=[self.order.id])

    @patch('shopify.services.payment_gateway.PaymentGateway.create_payment_intent')
    def test_create_payment_intent_success(self, mock_create):
        mock_create.return_value = {
            'client_secret': 'secret_123',
            'payment_intent_id': 'pi_123456'
        }

        response = self.client.post(self.payment_intent_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['client_secret'], 'secret_123')
        self.assertEqual(response.data['payment_intent_id'], 'pi_123456')

    @patch('shopify.services.payment_gateway.PaymentGateway.create_payment_intent')
    def test_create_payment_intent_failure(self, mock_create):
        mock_create.side_effect = PaymentError('Invalid currency')

        response = self.client.post(self.payment_intent_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid currency')

    @patch('shopify.services.payment_gateway.PaymentGateway.confirm_payment')
    def test_confirm_payment_success(self, mock_confirm):
        mock_confirm.return_value = True
        
        response = self.client.post(
            self.confirm_payment_url,
            {'payment_intent_id': 'pi_123456'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'payment_confirmed')
        
        # Check payment attempt was created
        payment = PaymentAttempt.objects.get(order=self.order)
        self.assertEqual(payment.status, 'COMPLETED')
        self.assertEqual(payment.payment_id, 'pi_123456')

    @patch('shopify.services.payment_gateway.PaymentGateway.confirm_payment')
    def test_confirm_payment_failure(self, mock_confirm):
        mock_confirm.return_value = False
        
        response = self.client.post(
            self.confirm_payment_url,
            {'payment_intent_id': 'pi_123456'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Payment confirmation failed')

    def test_confirm_payment_missing_intent_id(self):
        response = self.client.post(self.confirm_payment_url, {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'payment_intent_id is required')

    def test_payment_flow_integration(self):
        # Test complete payment flow
        with patch('shopify.services.payment_gateway.PaymentGateway.create_payment_intent') as mock_create:
            mock_create.return_value = {
                'client_secret': 'secret_123',
                'payment_intent_id': 'pi_123456'
            }
            
            # Step 1: Create payment intent
            response = self.client.post(self.payment_intent_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            payment_intent_id = response.data['payment_intent_id']
            
            # Step 2: Confirm payment
            with patch('shopify.services.payment_gateway.PaymentGateway.confirm_payment') as mock_confirm:
                mock_confirm.return_value = True
                
                response = self.client.post(
                    self.confirm_payment_url,
                    {'payment_intent_id': payment_intent_id}
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Step 3: Verify order status
            self.order.refresh_from_db()
            self.assertEqual(self.order.status, 'COMPLETED') 