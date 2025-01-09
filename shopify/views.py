from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
import json
from .models import ShopifyOrder, PaymentAttempt
from .services.shopify_client import ShopifyClient
from .services.pdf_generator import PDFGenerator
from .services.error_handler import handle_pdf_errors
import logging
from .services.cache_manager import PDFCacheManager
from .services.batch_pdf_generator import BatchPDFGenerator
from .services.email_service import EmailService

logger = logging.getLogger(__name__)
cache_manager = PDFCacheManager()

def home(request):
    """Home page view"""
    return render(request, 'shopify/home.html')

@csrf_exempt
@require_http_methods(["GET", "POST"])
def initiate_payment(request):
    """Creates a new order and initiates the payment process"""
    if request.method == "GET":
        # Render the payment initiation form
        return render(request, 'shopify/initiate_payment.html')
        
    # Handle POST request
    try:
        data = json.loads(request.body)
        order = ShopifyOrder.objects.create(**data)
        
        # Generate PDF
        pdf_generator = PDFGenerator()
        pdf_file = pdf_generator.generate_order_pdf(data)
        
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'pdf_file': pdf_file
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
def webhook(request):
    """Handles Shopify webhook callbacks for payment status updates"""
    try:
        data = json.loads(request.body)
        order = ShopifyOrder.objects.get(shopify_order_id=data.get('id'))
        
        if data.get('financial_status') == 'paid':
            order.status = 'PAID'
        elif data.get('financial_status') == 'failed':
            order.status = 'FAILED'
            
        order.save()
        return JsonResponse({'success': True})
        
    except ShopifyOrder.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def payment_success(request):
    """Handles successful payment redirect"""
    order_id = request.GET.get('order_id')
    try:
        order = ShopifyOrder.objects.get(id=order_id)
        return render(request, 'shopify/payment_success.html', {'order': order})
    except ShopifyOrder.DoesNotExist:
        return redirect('shopify:payment_error')

def payment_error(request):
    """Handles failed payment redirect"""
    return render(request, 'shopify/payment_error.html')

@handle_pdf_errors
def download_labels(request, order_id):
    """Generates and serves PDF for download"""
    order = ShopifyOrder.objects.get(id=order_id)
    pdf_generator = PDFGenerator()
    
    try:
        pdf_data = pdf_generator.generate_sample_labels(order.order_data)
    except Exception as e:
        logger.error(f"Failed to generate PDF for order {order_id}: {str(e)}")
        raise PDFGenerationError(f"Could not generate PDF for order {order_id}")
    
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sample_labels_{order.order_reference}.pdf"'
    return response

def print_labels(request, order_id):
    """
    Generates and serves PDF for printing
    """
    try:
        order = ShopifyOrder.objects.get(id=order_id)
        
        # Generate PDF
        pdf_generator = PDFGenerator()
        pdf_data = pdf_generator.generate_sample_labels(order.order_data)
        
        # Serve the PDF with print-friendly headers
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = 'inline'
        return response
        
    except ShopifyOrder.DoesNotExist:
        return HttpResponse('Order not found', status=404)
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return HttpResponse('Error generating PDF', status=500)

@handle_pdf_errors
def preview_pdf(request, order_id):
    """Renders PDF preview in browser"""
    order = ShopifyOrder.objects.get(id=order_id)
    
    # Try to get from cache first
    pdf_data = cache_manager.get_pdf(order_id)
    
    if not pdf_data:
        # Generate new PDF
        pdf_generator = PDFGenerator()
        pdf_data = pdf_generator.generate_sample_labels(order.order_data)
        cache_manager.save_pdf(order_id, pdf_data)
    
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = 'inline'
    return response

@require_POST
def email_pdf(request, order_id):
    """Emails PDF to specified recipients"""
    try:
        order = ShopifyOrder.objects.get(id=order_id)
        pdf_data = cache_manager.get_pdf(order_id) or PDFGenerator().generate_sample_labels(order.order_data)
        
        success = EmailService.send_pdf_email(
            order.customer_email,
            order.order_reference,
            pdf_data
        )
        
        return JsonResponse({'success': success})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def batch_download(request):
    """Handles batch PDF generation and download"""
    order_ids = request.POST.getlist('order_ids')
    
    generator = BatchPDFGenerator()
    pdf_data = generator.generate_batch_pdf(order_ids)
    
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="batch_labels.pdf"'
    return response

def payment_form(request, order_id):
    order = get_object_or_404(ShopifyOrder, id=order_id)
    return render(request, 'shopify/payment_form.html', {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY
    })
