from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from shopify.models import ShopifyOrder, PaymentAttempt
from unittest.mock import patch
import json

class APITests(APITestCase):
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create test order
        self.order = ShopifyOrder.objects.create(
            order_reference="TEST123",
            amount=100.00,
            currency="USD",
            customer_email="test@example.com",
            customer_name="Test User"
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)

    @patch('shopify.api.views.PDFGenerator')
    def test_generate_pdf(self, mock_pdf_generator):
        """Test PDF generation endpoint"""
        # Mock the PDF generator
        mock_instance = mock_pdf_generator.return_value
        mock_instance.generate_order_pdf.return_value = '/path/to/test.pdf'

        url = reverse('api:order-pdf-generate', args=[self.order.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pdf_url', response.data)
        self.assertEqual(response.data['pdf_url'], '/path/to/test.pdf')

    @patch('shopify.api.views.PDFGenerator')
    def test_batch_operations(self, mock_pdf_generator):
        """Test batch PDF generation"""
        # Mock the PDF generator
        mock_instance = mock_pdf_generator.return_value
        mock_instance.generate_order_pdf.return_value = '/path/to/test.pdf'

        url = reverse('api:batch-pdf-generate')
        data = {
            'order_ids': [self.order.id]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pdf_urls', response.data)
        self.assertEqual(response.data['pdf_urls'], ['/path/to/test.pdf'])

    def test_list_orders(self):
        """Test retrieving order list"""
        url = reverse('api:order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_order(self):
        """Test creating a new order"""
        url = reverse('api:order-list')
        data = {
            'order_reference': 'TEST456',
            'amount': 200.00,
            'currency': 'USD',
            'customer_email': 'test2@example.com',
            'customer_name': 'Test User 2'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ShopifyOrder.objects.count(), 2)

class PaymentAPITests(APITestCase):
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create test order and payment
        self.order = ShopifyOrder.objects.create(
            order_reference="TEST123",
            amount=100.00,
            currency="USD"
        )
        self.payment = PaymentAttempt.objects.create(
            order=self.order,
            amount=100.00,
            status='INITIATED'
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)

    def test_list_payments(self):
        """Test getting list of payments"""
        url = reverse('api:payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_payment_detail(self):
        """Test getting single payment details"""
        url = reverse('api:payment-detail', args=[self.payment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK) 