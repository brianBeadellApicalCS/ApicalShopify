import shopify
from django.conf import settings
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ShopifyClient:
    """
    Service class to handle all Shopify API interactions
    """
    def __init__(self):
        # Initialize Shopify API connection
        shopify.Session.setup(
            api_key=settings.SHOPIFY_SETTINGS['ACCESS_TOKEN'],
            secret=settings.SHOPIFY_SETTINGS['API_SECRET']
        )
        
        self.session = shopify.Session(
            shop_url=settings.SHOPIFY_SETTINGS['SHOP_NAME'],
            version=settings.SHOPIFY_SETTINGS['API_VERSION'],
            token=settings.SHOPIFY_SETTINGS['ACCESS_TOKEN']
        )
        shopify.ShopifyResource.activate_session(self.session)

    def create_payment_session(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a payment session in Shopify
        
        Args:
            order_data: Dictionary containing order information
                {
                    'order_reference': 'ABC123',
                    'amount': '100.00',
                    'currency': 'USD',
                    'customer_email': 'example@email.com',
                    'customer_name': 'John Doe',
                    'items': [...]
                }
        
        Returns:
            Dictionary containing payment session details
                {
                    'success': True/False,
                    'payment_url': 'https://...',
                    'shopify_order_id': '12345',
                    'error': 'Error message if any'
                }
        """
        try:
            # Create order in Shopify
            order = shopify.Order()
            
            # Set basic order details
            order.email = order_data['customer_email']
            order.reference = order_data['order_reference']
            
            # Add line items
            order.line_items = self._format_line_items(order_data.get('items', []))
            
            # Add customer details
            customer = self._get_or_create_customer(order_data)
            if customer:
                order.customer = customer

            # Save the order
            if order.save():
                # Create payment session
                payment_session = order.create_payment_session()
                
                return {
                    'success': True,
                    'payment_url': payment_session.payment_url,
                    'shopify_order_id': str(order.id)
                }
            
            return {
                'success': False,
                'error': order.errors.full_messages()
            }

        except Exception as e:
            logger.error(f"Error creating Shopify payment session: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def verify_webhook(self, data: bytes, hmac_header: str) -> bool:
        """
        Verifies Shopify webhook signature
        """
        return shopify.WebhookVerification.verify(
            data, 
            hmac_header, 
            settings.SHOPIFY_SETTINGS['API_SECRET']
        )

    def get_order_status(self, order_id: str) -> Optional[str]:
        """
        Retrieves the current status of a Shopify order
        """
        try:
            order = shopify.Order.find(order_id)
            return order.financial_status
        except Exception as e:
            logger.error(f"Error fetching order status: {str(e)}")
            return None

    def _format_line_items(self, items: list) -> list:
        """
        Formats order items for Shopify API
        """
        return [
            {
                'title': item.get('name', 'Unknown Item'),
                'quantity': item.get('quantity', 1),
                'price': item.get('price', '0.00'),
                'requires_shipping': False,  # Since these are lab tests
                'taxable': False  # Adjust based on your needs
            }
            for item in items
        ]

    def _get_or_create_customer(self, order_data: Dict[str, Any]) -> Optional[Any]:
        """
        Finds or creates a customer in Shopify
        """
        try:
            # Search for existing customer
            customers = shopify.Customer.find(
                email=order_data['customer_email']
            )
            
            if customers:
                return customers[0]
            
            # Create new customer
            customer = shopify.Customer()
            customer.email = order_data['customer_email']
            customer.first_name = order_data['customer_name'].split()[0]
            customer.last_name = ' '.join(order_data['customer_name'].split()[1:])
            
            if customer.save():
                return customer
                
            return None
            
        except Exception as e:
            logger.error(f"Error handling customer: {str(e)}")
            return None

    def __del__(self):
        """
        Cleanup Shopify session
        """
        shopify.ShopifyResource.clear_session() 