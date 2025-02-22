from django.core.cache import cache
from django.db.models import Prefetch
from django.conf import settings
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Manage caching operations"""
    
    CACHE_TIMES = {
        'parking_lot': 3600,  # 1 hour
        'booking': 300,       # 5 minutes
        'user': 1800,        # 30 minutes
        'stats': 900         # 15 minutes
    }

    @staticmethod
    def cache_key(prefix, identifier):
        return f"{prefix}:{identifier}"

    @staticmethod
    def cached_query(prefix, identifier, query_func, timeout=None):
        """Execute cached database query"""
        key = CacheManager.cache_key(prefix, identifier)
        result = cache.get(key)
        
        if result is None:
            result = query_func()
            cache.set(key, result, timeout or CacheManager.CACHE_TIMES.get(prefix, 300))
            
        return result

    @staticmethod
    def invalidate_cache(prefix, identifier=None):
        """Invalidate specific cache or pattern"""
        if identifier:
            # Delete specific key
            cache.delete(CacheManager.cache_key(prefix, identifier))
        else:
            # Delete all keys with prefix
            keys = cache.keys(f"{prefix}:*") if hasattr(cache, 'keys') else []
            for key in keys:
                cache.delete(key)

def cache_response(timeout=None):
    """Decorator for caching view responses"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Generate cache key based on request
            cache_key = f"view:{request.path}:{request.user.id}:{hash(frozenset(request.GET.items()))}"
            response = cache.get(cache_key)
            
            if response is None:
                response = view_func(request, *args, **kwargs)
                cache.set(cache_key, response, timeout)
                
            return response
        return wrapper
    return decorator

class QueryOptimizer:
    """Optimize database queries"""
    
    @staticmethod
    def optimize_parking_lot_query(queryset):
        """Optimize parking lot queries with related data"""
        return queryset.prefetch_related(
            Prefetch('bookings', to_attr='active_bookings'),
            'amenities',
            'reviews'
        ).select_related('owner')

    @staticmethod
    def optimize_booking_query(queryset):
        """Optimize booking queries"""
        return queryset.select_related(
            'user',
            'parking_lot'
        ).prefetch_related('payments')

def measure_execution_time(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        logger.info(f"{func.__name__} execution time: {execution_time:.4f} seconds")
        return result
    return wrapper

class DatabaseOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def chunk_queryset(queryset, chunk_size=1000):
        """Process large querysets in chunks"""
        offset = 0
        while True:
            chunk = queryset[offset:offset + chunk_size]
            if not chunk:
                break
            yield chunk
            offset += chunk_size

    @staticmethod
    def bulk_create_with_progress(model, objects, batch_size=100):
        """Bulk create with progress tracking"""
        total = len(objects)
        created = 0
        
        for i in range(0, total, batch_size):
            batch = objects[i:i + batch_size]
            model.objects.bulk_create(batch)
            created += len(batch)
            logger.info(f"Progress: {created}/{total} records created") 