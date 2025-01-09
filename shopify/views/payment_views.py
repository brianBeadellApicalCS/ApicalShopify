from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import ShopifyOrder, PaymentAttempt
from ..services.payment_gateway import PaymentGateway, PaymentError
from ..decorators.security import (
    require_https,
    rate_limit,
    require_idempotency,
    validate_payment_data,
    require_permission_level,
    log_payment_activity
)

@api_view(['POST'])
@require_https
@rate_limit(requests=100, interval=60)
@require_idempotency
@validate_payment_data
@log_payment_activity
def create_payment_intent(request, order_id):
    order = get_object_or_404(ShopifyOrder, id=order_id)
    gateway = PaymentGateway()
    
    try:
        result = gateway.create_payment_intent(order)
        return Response(result)
    except PaymentError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@require_https
@rate_limit(requests=50, interval=60)
@require_idempotency
@validate_payment_data
@log_payment_activity
def confirm_payment(request, order_id):
    order = get_object_or_404(ShopifyOrder, id=order_id)
    payment_intent_id = request.data.get('payment_intent_id')
    
    if not payment_intent_id:
        return Response(
            {'error': 'payment_intent_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    gateway = PaymentGateway()
    
    try:
        success = gateway.confirm_payment(payment_intent_id)
        if success:
            PaymentAttempt.objects.create(
                order=order,
                amount=order.amount,
                status='COMPLETED',
                payment_method='card',
                payment_id=payment_intent_id
            )
            return Response({'status': 'payment_confirmed'})
        return Response(
            {'error': 'Payment confirmation failed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except PaymentError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        ) 

@api_view(['POST'])
@require_https
@rate_limit(requests=20, interval=60)
@require_idempotency
@require_permission_level('admin')
@log_payment_activity
def refund_payment(request, payment_id):
    payment = get_object_or_404(PaymentAttempt, id=payment_id)
    amount = request.data.get('amount', payment.amount)
    
    try:
        payment.refund(amount)
        return Response({'status': 'refund_processed'})
    except ValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        ) 