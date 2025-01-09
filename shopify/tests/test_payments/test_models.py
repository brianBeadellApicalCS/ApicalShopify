from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from ...models import ShopifyOrder, PaymentAttempt

class PaymentAttemptTests(TestCase):
    def setUp(self):
        self.order = ShopifyOrder.objects.create(
            order_reference='TEST123',
            amount=Decimal('100.00'),
            currency='USD',
            customer_email='test@example.com',
            customer_name='Test User',
            order_data={'line_items': []}
        )

    def test_payment_attempt_creation(self):
        payment = PaymentAttempt.objects.create(
            order=self.order,
            amount=Decimal('100.00'),
            status='INITIATED',
            payment_method='card',
            payment_id='pi_123456',
            metadata={'stripe_intent_id': 'pi_123456'}
        )
        self.assertEqual(payment.status, 'INITIATED')
        self.assertEqual(payment.amount, Decimal('100.00'))

    def test_payment_attempt_status_update(self):
        payment = PaymentAttempt.objects.create(
            order=self.order,
            amount=Decimal('100.00'),
            status='INITIATED',
            payment_method='card'
        )
        payment.status = 'COMPLETED'
        payment.save()
        
        self.assertEqual(payment.status, 'COMPLETED')
        self.assertEqual(self.order.status, 'COMPLETED')

    def test_payment_amount_validation(self):
        with self.assertRaises(ValidationError):
            PaymentAttempt.objects.create(
                order=self.order,
                amount=Decimal('150.00'),  # Exceeds order amount
                status='INITIATED',
                payment_method='card'
            ) 