import logging
from functools import wraps
from typing import Callable, Any
from django.http import HttpResponse, JsonResponse

logger = logging.getLogger(__name__)

class PDFGenerationError(Exception):
    """Custom exception for PDF generation errors"""
    pass

def handle_pdf_errors(func: Callable) -> Callable:
    """Decorator for handling PDF generation errors"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except PDFGenerationError as e:
            logger.error(f"PDF Generation Error: {str(e)}", exc_info=True)
            return HttpResponse(
                'Error generating PDF: Please try again later', 
                status=500
            )
        except Exception as e:
            logger.critical(
                f"Unexpected error in PDF generation: {str(e)}", 
                exc_info=True
            )
            return HttpResponse(
                'An unexpected error occurred', 
                status=500
            )
    return wrapper 