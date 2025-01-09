from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from shopify.models import ShopifyOrder, PaymentAttempt
from unittest.mock import patch
import json

class IntegrationTests(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)

    def test_order_payment_flow(self):
        """Test complete order and payment flow"""
        # 1. Create order
        order_url = reverse('api:order-list')
        order_data = {
            'order_reference': 'TEST123',
            'amount': '100.00',
            'currency': 'USD',
            'customer_email': 'test@example.com',
            'customer_name': 'Test User',
            'order_data': {'line_items': []}
        }
        response = self.client.post(order_url, order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id = response.data['id']

        # 2. Generate PDF for order
        with patch('shopify.api.views.PDFGenerator') as mock_pdf_generator:
            mock_instance = mock_pdf_generator.return_value
            mock_instance.generate_order_pdf.return_value = '/path/to/test.pdf'
            
            pdf_url = reverse('api:order-pdf-generate', args=[order_id])
            response = self.client.post(pdf_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('pdf_url', response.data)

        # 3. Create payment for order
        payment_url = reverse('api:payment-list')
        payment_data = {
            'order': order_id,
            'amount': '100.00',
            'status': 'INITIATED',
            'payment_method': 'card'
        }
        response = self.client.post(payment_url, payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payment_id = response.data['id']

        # 4. Verify order details
        order_detail_url = reverse('api:order-detail', args=[order_id])
        response = self.client.get(order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_reference'], 'TEST123')

        # 5. Verify payment details
        payment_detail_url = reverse('api:payment-detail', args=[payment_id])
        response = self.client.get(payment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'INITIATED')

    def test_batch_operations_flow(self):
        """Test batch operations flow"""
        # 1. Create multiple orders
        orders = []
        for i in range(3):
            order = ShopifyOrder.objects.create(
                order_reference=f"TEST{i}",
                amount=100.00,
                currency="USD",
                customer_email=f"test{i}@example.com",
                customer_name=f"Test User {i}",
                status='PENDING',
                order_data={}
            )
            orders.append(order)

        # 2. Generate PDFs in batch
        with patch('shopify.api.views.PDFGenerator') as mock_pdf_generator:
            mock_instance = mock_pdf_generator.return_value
            mock_instance.generate_order_pdf.return_value = '/path/to/test.pdf'
            
            url = reverse('api:batch-pdf-generate')
            data = {
                'order_ids': [order.id for order in orders]
            }
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['pdf_urls']), 3)

        # 3. Verify all orders
        for order in orders:
            url = reverse('api:order-detail', args=[order.id])
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK) 