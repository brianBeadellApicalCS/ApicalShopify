from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from typing import List
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Handles sending PDFs via email"""
    
    @staticmethod
    def send_pdf_email(
        email: str,
        order_reference: str,
        pdf_data: bytes,
        additional_recipients: List[str] = None
    ) -> bool:
        try:
            # Create email message
            subject = f"Sample Labels - Order {order_reference}"
            
            # Render HTML email template
            html_content = render_to_string(
                'shopify/emails/pdf_email.html',
                {'order_reference': order_reference}
            )
            
            # Create email
            email = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email] + (additional_recipients or [])
            )
            
            # Attach PDF
            email.attach(
                f'sample_labels_{order_reference}.pdf',
                pdf_data,
                'application/pdf'
            )
            
            # Send email
            email.send()
            return True
            
        except Exception as e:
            logger.error(f"Error sending PDF email: {str(e)}")
            return False 