from django.contrib import admin
from .models import ShopifyOrder, PaymentAttempt

@admin.register(ShopifyOrder)
class ShopifyOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_reference', 'amount', 'currency', 'customer_name', 'created_at')
    list_filter = ('currency', 'created_at')
    search_fields = ('order_reference', 'customer_email', 'customer_name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order__order_reference', 'payment_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('order', 'amount')
        return self.readonly_fields
