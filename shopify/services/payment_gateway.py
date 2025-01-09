from typing import Dict, Any
import stripe
from django.conf import settings
from ..models import ShopifyOrder, PaymentAttempt

class PaymentGateway:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_payment_intent(self, order: ShopifyOrder) -> Dict[str, Any]:
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(order.amount * 100),  # Convert to cents
                currency=order.currency.lower(),
                metadata={'order_reference': order.order_reference}
            )
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            }
        except stripe.error.StripeError as e:
            raise PaymentError(str(e))

    def confirm_payment(self, payment_intent_id: str) -> bool:
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return intent.status == 'succeeded'
        except stripe.error.StripeError as e:
            raise PaymentError(str(e))

class PaymentError(Exception):
    pass 