from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from django.core import mail
from ..models import ShopifyOrder, PDFTemplate
from ..services.cache_manager import PDFCacheManager
from ..services.batch_pdf_generator import BatchPDFGenerator
from ..services.email_service import EmailService
import json

class PDFFeatureTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cache_manager = PDFCacheManager()
        
        # Create test orders
        self.order1 = ShopifyOrder.objects.create(
            order_reference='TEST-001',
            amount=100.00,
            customer_email='test1@example.com',
            customer_name='Test User 1',
            order_data={
                'fields': [{
                    'name': 'Field 1',
                    'crops': [{
                        'name': 'Corn',
                        'cultivars': [{
                            'name': 'Sweet Corn 1',
                            'sample_id': 'SC001'
                        }]
                    }]
                }]
            }
        )
        
        self.order2 = ShopifyOrder.objects.create(
            order_reference='TEST-002',
            amount=200.00,
            customer_email='test2@example.com',
            customer_name='Test User 2',
            order_data={
                'fields': [{
                    'name': 'Field 2',
                    'crops': [{
                        'name': 'Wheat',
                        'cultivars': [{
                            'name': 'Winter Wheat 1',
                            'sample_id': 'WW001'
                        }]
                    }]
                }]
            }
        ) 