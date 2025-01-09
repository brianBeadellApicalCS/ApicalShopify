from rest_framework import serializers
from ..models import ShopifyOrder, PaymentAttempt

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopifyOrder
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAttempt
        fields = '__all__'
        read_only_fields = ('payment_id', 'error_message')

    def validate(self, data):
        """
        Check that the payment amount matches the order amount
        """
        if data['amount'] != data['order'].amount:
            raise serializers.ValidationError({
                'amount': 'Payment amount must match order amount'
            })
        return data
