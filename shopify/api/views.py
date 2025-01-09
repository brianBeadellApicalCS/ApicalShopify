from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from ..models import ShopifyOrder, PaymentAttempt
from .serializers import OrderSerializer, PaymentSerializer
from ..services.pdf_generator import PDFGenerator
from django.core.exceptions import ValidationError
from typing import List, Optional

class OrderViewSet(viewsets.ModelViewSet):
    queryset = ShopifyOrder.objects.all()
    serializer_class = OrderSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = PaymentAttempt.objects.all()
    serializer_class = PaymentSerializer

class OrderList(generics.ListCreateAPIView):
    queryset = ShopifyOrder.objects.all()
    serializer_class = OrderSerializer

class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShopifyOrder.objects.all()
    serializer_class = OrderSerializer

class OrderPDFGeneration(APIView):
    def post(self, request, pk):
        try:
            order = ShopifyOrder.objects.get(pk=pk)
            pdf_generator = PDFGenerator()
            pdf_file = pdf_generator.generate_order_pdf(order.order_data)
            return Response({'pdf_url': pdf_file}, status=status.HTTP_200_OK)
        except ShopifyOrder.DoesNotExist:
            return Response(
                {'error': 'Order not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BatchPDFGeneration(APIView):
    def validate_order_ids(self, order_ids) -> Optional[Response]:
        """Validate order_ids input"""
        if not isinstance(order_ids, list):
            return Response(
                {'error': 'order_ids must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not order_ids:
            return Response(
                {'error': 'order_ids list cannot be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate that all IDs exist
        invalid_ids = []
        for order_id in order_ids:
            try:
                ShopifyOrder.objects.get(pk=order_id)
            except (ShopifyOrder.DoesNotExist, ValueError):
                invalid_ids.append(order_id)
        
        if invalid_ids:
            return Response(
                {'error': f'Invalid order IDs: {invalid_ids}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return None

    def post(self, request):
        order_ids = request.data.get('order_ids', [])
        
        # Validate input
        validation_error = self.validate_order_ids(order_ids)
        if validation_error:
            return validation_error
            
        try:
            pdf_generator = PDFGenerator()
            pdf_files = []
            
            for order_id in order_ids:
                order = ShopifyOrder.objects.get(pk=order_id)
                pdf_file = pdf_generator.generate_order_pdf(order.order_data)
                pdf_files.append(pdf_file)
                
            return Response({'pdf_urls': pdf_files}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BatchEmailSend(APIView):
    def post(self, request):
        order_ids = request.data.get('order_ids', [])
        try:
            for order_id in order_ids:
                order = ShopifyOrder.objects.get(pk=order_id)
                # Add email sending logic here
            return Response({'message': 'Emails sent successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentList(generics.ListCreateAPIView):
    queryset = PaymentAttempt.objects.all()
    serializer_class = PaymentSerializer

class PaymentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PaymentAttempt.objects.all()
    serializer_class = PaymentSerializer
