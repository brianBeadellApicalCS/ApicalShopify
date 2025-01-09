from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime

class ShopifyOrder(models.Model):
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]

    ALLOWED_CURRENCIES = ['USD', 'EUR', 'GBP', 'CAD', 'AUD']

    order_reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(max_length=3)
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_reference']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.order_reference} - {self.amount} {self.currency}"

    def clean(self):
        if self.currency not in self.ALLOWED_CURRENCIES:
            raise ValidationError({'currency': f'Currency must be one of {", ".join(self.ALLOWED_CURRENCIES)}'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_paid(self):
        return self.payments.filter(status='COMPLETED').exists()

    @property
    def total_paid(self):
        return self.payments.filter(status='COMPLETED').aggregate(
            total=models.Sum('amount'))['total'] or Decimal('0.00')

    @property
    def payment_status(self):
        if self.total_paid >= self.amount:
            return 'PAID'
        elif self.total_paid > 0:
            return 'PARTIALLY_PAID'
        return 'UNPAID'

    def can_cancel(self):
        return self.status not in ['COMPLETED', 'CANCELLED', 'REFUNDED']

    def cancel(self):
        if not self.can_cancel():
            raise ValidationError('Order cannot be cancelled in its current state')
        self.status = 'CANCELLED'
        self.save()

class PaymentAttempt(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('INITIATED', 'Initiated'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    order = models.ForeignKey(ShopifyOrder, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='INITIATED')
    payment_method = models.CharField(max_length=50, default='card')
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict, blank=True)  # For additional payment data

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['payment_method']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.order_reference}"

    def clean(self):
        if self.amount > self.order.amount:
            raise ValidationError({'amount': 'Payment amount cannot exceed order amount'})
        
        if self.order.status in ['CANCELLED', 'REFUNDED']:
            raise ValidationError('Cannot process payment for cancelled or refunded order')

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.pk:  # New payment attempt
            if self.status == 'COMPLETED':
                self.order.status = 'COMPLETED'
                self.order.save()
        super().save(*args, **kwargs)

    def can_refund(self):
        return self.status == 'COMPLETED'

    def refund(self, amount=None):
        if not self.can_refund():
            raise ValidationError('Payment cannot be refunded in its current state')
        
        refund_amount = amount or self.amount
        if refund_amount > self.amount:
            raise ValidationError('Refund amount cannot exceed payment amount')
        
        self.status = 'REFUNDED'
        self.save()
        
        # If this was the only payment and it's fully refunded
        if refund_amount == self.amount and not self.order.payments.exclude(id=self.id).exists():
            self.order.status = 'REFUNDED'
            self.order.save()