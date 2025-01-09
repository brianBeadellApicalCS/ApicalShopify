class PaymentService:
    def create_payment(self, order, payment_method):
        """
        Create a new payment attempt
        """
        return PaymentAttempt.objects.create(
            order=order,
            amount=order.amount,
            payment_method=payment_method
        )

    def process_payment(self, payment_attempt):
        """
        Process the payment attempt
        """
        try:
            # Add your payment processing logic here
            payment_attempt.status = 'SUCCEEDED'
            payment_attempt.save()
            return True
        except Exception as e:
            payment_attempt.status = 'FAILED'
            payment_attempt.error_message = str(e)
            payment_attempt.save()
            return False 