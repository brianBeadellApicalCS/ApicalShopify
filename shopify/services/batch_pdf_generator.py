from typing import List, Dict
from PyPDF2 import PdfMerger
import io
from .pdf_generator import PDFGenerator
from ..models import ShopifyOrder
import logging

logger = logging.getLogger(__name__)

class BatchPDFGenerator:
    """Handles generation of PDFs for multiple orders"""
    
    def __init__(self):
        self.pdf_generator = PDFGenerator()

    def generate_batch_pdf(self, order_ids: List[int]) -> bytes:
        """
        Generates a single PDF containing labels for multiple orders
        """
        merger = PdfMerger()
        
        try:
            for order_id in order_ids:
                order = ShopifyOrder.objects.get(id=order_id)
                pdf_data = self.pdf_generator.generate_sample_labels(order.order_data)
                
                # Add the PDF to the merger
                pdf_buffer = io.BytesIO(pdf_data)
                merger.append(pdf_buffer)
            
            # Create the final merged PDF
            output = io.BytesIO()
            merger.write(output)
            merger.close()
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error in batch PDF generation: {str(e)}")
            raise 