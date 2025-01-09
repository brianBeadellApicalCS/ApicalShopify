from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from ...models import ShopifyOrder, PaymentAttempt

class PaymentEdgeCaseTests(TestCase):
    def setUp(self):
        self.order = ShopifyOrder.objects.create(
            order_reference='TEST123',
            amount=Decimal('100.00'),
            currency='USD',
            customer_email='test@example.com',
            customer_name='Test User',
            order_data={'line_items': []}
        )

    def test_multiple_payments_validation(self):
        # Create first payment
        PaymentAttempt.objects.create(
            order=self.order,
            amount=Decimal('50.00'),
            status='COMPLETED',
            payment_method='card'
        )

        # Try to create second payment exceeding total
        with self.assertRaises(ValidationError):
            PaymentAttempt.objects.create(
                order=self.order,
                amount=Decimal('60.00'),  # Would exceed order amount
                status='INITIATED',
                payment_method='card'
            )

    def test_cancelled_order_payment(self):
        self.order.status = 'CANCELLED'
        self.order.save()

        with self.assertRaises(ValidationError):
            PaymentAttempt.objects.create(
                order=self.order,
                amount=Decimal('100.00'),
                status='INITIATED',
                payment_method='card'
            )

    def test_zero_amount_payment(self):
        with self.assertRaises(ValidationError):
            PaymentAttempt.objects.create(
                order=self.order,
                amount=Decimal('0.00'),
                status='INITIATED',
                payment_method='card'
            )

    def test_negative_amount_payment(self):
        with self.assertRaises(ValidationError):
            PaymentAttempt.objects.create(
                order=self.order,
                amount=Decimal('-50.00'),
                status='INITIATED',
                payment_method='card'
            )

    def test_refund_completed_payment(self):
        payment = PaymentAttempt.objects.create(
            order=self.order,
            amount=Decimal('100.00'),
            status='COMPLETED',
            payment_method='card'
        )
        
        payment.status = 'REFUNDED'
        payment.save()
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'REFUNDED') 