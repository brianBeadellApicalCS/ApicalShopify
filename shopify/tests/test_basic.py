from django.test import TestCase
from shopify.models import ShopifyOrder

class BasicTests(TestCase):
    def setUp(self):
        self.order = ShopifyOrder.objects.create(
            order_reference="TEST123",
            amount=100.00,
            currency="USD",
            customer_email="test@example.com",
            customer_name="Test User"
        )

    def test_order_creation(self):
        """Test basic order creation"""
        self.assertEqual(self.order.order_reference, "TEST123")
        self.assertEqual(self.order.amount, 100.00) 