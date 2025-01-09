from functools import wraps
from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
import hashlib
import time

def require_https(view_func):
    """Ensure the request is using HTTPS"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.is_secure() and not settings.DEBUG:
            return Response(
                {'error': 'HTTPS is required for this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        return view_func(request, *args, **kwargs)
    return wrapper

def rate_limit(requests=100, interval=60):
    """Rate limit based on user IP or ID"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get identifier (user ID or IP)
            if request.user.is_authenticated:
                identifier = f"rate_limit_user_{request.user.id}"
            else:
                identifier = f"rate_limit_ip_{request.META.get('REMOTE_ADDR')}"
            
            # Check cache for rate limit
            cache_key = f"{identifier}_{view_func.__name__}"
            requests_made = cache.get(cache_key, 0)
            
            if requests_made >= requests:
                return Response(
                    {'error': 'Rate limit exceeded'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Increment request count
            cache.set(cache_key, requests_made + 1, interval)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_idempotency(view_func):
    """Ensure idempotent requests using idempotency key"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method not in ['POST', 'PUT', 'PATCH']:
            return view_func(request, *args, **kwargs)
            
        idempotency_key = request.headers.get('X-Idempotency-Key')
        if not idempotency_key:
            return Response(
                {'error': 'Idempotency key required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create cache key from request data
        cache_key = f"idempotency_{idempotency_key}"
        cached_response = cache.get(cache_key)
        
        if cached_response:
            return cached_response
            
        response = view_func(request, *args, **kwargs)
        cache.set(cache_key, response, 86400)  # Cache for 24 hours
        return response
    return wrapper

def validate_payment_data(view_func):
    """Validate payment-related data"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            amount = request.data.get('amount')
            if amount and float(amount) <= 0:
                return Response(
                    {'error': 'Invalid payment amount'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            payment_method = request.data.get('payment_method')
            if payment_method and payment_method not in ['card', 'bank_transfer']:
                return Response(
                    {'error': 'Invalid payment method'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return view_func(request, *args, **kwargs)
    return wrapper

def require_permission_level(permission_level):
    """Check for specific permission level"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
            if permission_level == 'admin' and not request.user.is_staff:
                raise PermissionDenied('Admin access required')
                
            if permission_level == 'staff' and not (request.user.is_staff or request.user.groups.filter(name='staff').exists()):
                raise PermissionDenied('Staff access required')
                
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def log_payment_activity(view_func):
    """Log all payment-related activities"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        start_time = time.time()
        response = view_func(request, *args, **kwargs)
        duration = time.time() - start_time
        
        # Log activity (implement your logging logic here)
        if hasattr(request, 'user'):
            user_id = request.user.id if request.user.is_authenticated else None
            activity_data = {
                'user_id': user_id,
                'endpoint': request.path,
                'method': request.method,
                'duration': duration,
                'status_code': response.status_code
            }
            # You can implement your logging mechanism here
            # e.g., using Django's logging framework
        
        return response
    return wrapper 