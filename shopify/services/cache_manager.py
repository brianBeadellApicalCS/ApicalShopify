from django.core.cache import cache
from django.conf import settings
import hashlib
from typing import Optional

class PDFCacheManager:
    """Manages caching of generated PDFs"""
    
    CACHE_TIMEOUT = getattr(settings, 'PDF_CACHE_TIMEOUT', 3600)  # 1 hour default
    
    @staticmethod
    def get_cache_key(order_id: int, template_version: str = '1.0') -> str:
        """Generate a unique cache key for the PDF"""
        key = f"pdf_order_{order_id}_v{template_version}"
        return hashlib.md5(key.encode()).hexdigest()

    def get_pdf(self, order_id: int) -> Optional[bytes]:
        """Retrieve PDF from cache"""
        cache_key = self.get_cache_key(order_id)
        return cache.get(cache_key)

    def save_pdf(self, order_id: int, pdf_data: bytes) -> None:
        """Save PDF to cache"""
        cache_key = self.get_cache_key(order_id)
        cache.set(cache_key, pdf_data, self.CACHE_TIMEOUT)

    def invalidate_pdf(self, order_id: int) -> None:
        """Remove PDF from cache"""
        cache_key = self.get_cache_key(order_id)
        cache.delete(cache_key) 