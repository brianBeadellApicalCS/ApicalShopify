from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from ..models import ShopifyOrder, PaymentAttempt

class ShopifyOrderTests(TestCase):
    def setUp(self):
        self.order = ShopifyOrder.objects.create(
            order_reference='TEST123',
            amount=Decimal('100.00'),
            currency='USD',
            customer_email='test@example.com',
            customer_name='Test User',
            order_data={'line_items': []}
        )

    def test_invalid_currency(self):
        with self.assertRaises(ValidationError):
            ShopifyOrder.objects.create(
                order_reference='TEST124',
                amount=Decimal('100.00'),
                currency='XXX',  # Invalid currency
                customer_email='test@example.com',
                customer_name='Test User',
                order_data={'line_items': []}
            )

    def test_payment_status(self):
        self.assertEqual(self.order.payment_status, 'UNPAID')
        
        # Add partial payment
        PaymentAttempt.objects.create(
            order=self.order,
            amount=Decimal('50.00'),
            status='COMPLETED'
        )
        self.assertEqual(self.order.payment_status, 'PARTIALLY_PAID')
        
        # Add remaining payment
        PaymentAttempt.objects.create(
            order=self.order,
            amount=Decimal('50.00'),
            status='COMPLETED'
        )
        self.assertEqual(self.order.payment_status, 'PAID')

    def test_cancel_order(self):
        self.assertTrue(self.order.can_cancel())
        self.order.cancel()
        self.assertEqual(self.order.status, 'CANCELLED')
        
        # Cannot cancel already cancelled order
        with self.assertRaises(ValidationError):
            self.order.cancel()

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

    def test_payment_amount_validation(self):
        with self.assertRaises(ValidationError):
            PaymentAttempt.objects.create(
                order=self.order,
                amount=Decimal('150.00'),  # Exceeds order amount
                status='INITIATED'
            )

    def test_refund_payment(self):
        payment = PaymentAttempt.objects.create(
            order=self.order,
            amount=Decimal('100.00'),
            status='COMPLETED'
        )
        
        self.assertTrue(payment.can_refund())
        payment.refund()
        self.assertEqual(payment.status, 'REFUNDED')
        self.assertEqual(self.order.status, 'REFUNDED') 