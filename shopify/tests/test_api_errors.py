from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from shopify.models import ShopifyOrder, PaymentAttempt
from unittest.mock import patch
import json

class APIErrorTests(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)

    def test_order_not_found(self):
        """Test 404 response for non-existent order"""
        url = reverse('api:order-detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_order_data(self):
        """Test creating order with invalid data"""
        url = reverse('api:order-list')
        data = {
            'order_reference': '',  # Empty reference
            'amount': 'invalid',    # Invalid amount
            'currency': 'INVALID'   # Invalid currency
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('shopify.api.views.PDFGenerator')
    def test_pdf_generation_failure(self, mock_pdf_generator):
        """Test PDF generation failure handling"""
        # Create test order
        order = ShopifyOrder.objects.create(
            order_reference="TEST123",
            amount=100.00,
            currency="USD"
        )
        
        # Mock PDF generator to raise an exception
        mock_instance = mock_pdf_generator.return_value
        mock_instance.generate_order_pdf.side_effect = Exception("PDF generation failed")

        url = reverse('api:order-pdf-generate', args=[order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)

    def test_unauthorized_access(self):
        """Test unauthorized access to API"""
        # Remove authentication
        self.client.force_authenticate(user=None)
        
        url = reverse('api:order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_batch_request(self):
        """Test batch operation with invalid data"""
        url = reverse('api:batch-pdf-generate')
        data = {
            'order_ids': 'not-a-list'  # Invalid format
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_validation(self):
        """Test payment creation with invalid amount"""
        order = ShopifyOrder.objects.create(
            order_reference="TEST123",
            amount=100.00,
            currency="USD"
        )
        
        url = reverse('api:payment-list')
        data = {
            'order': order.id,
            'amount': -50.00,  # Negative amount
            'status': 'INVALID_STATUS'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 