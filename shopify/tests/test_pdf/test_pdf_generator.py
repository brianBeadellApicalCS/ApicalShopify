from django.test import TestCase
from django.core.files.base import ContentFile
import PyPDF2
import io
from ..services.pdf_generator import PDFGenerator

class PDFGeneratorTests(TestCase):
    def setUp(self):
        self.pdf_generator = PDFGenerator()
        self.sample_order_data = {
            'order_reference': 'TEST-001',
            'customer_name': 'John Doe',
            'customer_email': 'john@example.com',
            'fields': [
                {
                    'name': 'Field 1',
                    'crops': [
                        {
                            'name': 'Corn',
                            'cultivars': [
                                {
                                    'name': 'Sweet Corn 1',
                                    'sample_id': 'SC001'
                                }
                            ]
                        }
                    ]
                }
            ]
        }

    def test_pdf_generation(self):
        # Generate PDF
        pdf_data = self.pdf_generator.generate_sample_labels(self.sample_order_data)
        
        # Verify PDF was generated
        self.assertIsInstance(pdf_data, bytes)
        
        # Verify PDF content
        pdf_file = io.BytesIO(pdf_data)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Check if PDF has at least one page
        self.assertGreater(len(pdf_reader.pages), 0)

    def test_pdf_generation_with_empty_data(self):
        empty_order = {
            'order_reference': 'TEST-002',
            'customer_name': 'Jane Doe',
            'customer_email': 'jane@example.com',
            'fields': []
        }
        
        # Should generate PDF without errors
        pdf_data = self.pdf_generator.generate_sample_labels(empty_order)
        self.assertIsInstance(pdf_data, bytes)

    def test_pdf_generation_error_handling(self):
        invalid_data = None
        
        with self.assertRaises(Exception):
            self.pdf_generator.generate_sample_labels(invalid_data) 