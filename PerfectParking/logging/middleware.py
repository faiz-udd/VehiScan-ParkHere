import logging
import time
import uuid
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('perfect_parking')

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.id = str(uuid.uuid4())
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            log_data = {
                'request_id': getattr(request, 'id', None),
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration': round(duration * 1000, 2),  # Convert to milliseconds
                'user_id': request.user.id if request.user.is_authenticated else None,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT'),
            }
            
            if response.status_code >= 400:
                logger.error('Request failed', extra=log_data)
            else:
                logger.info('Request completed', extra=log_data)
                
        return response 