

from django.http import JsonResponse
from rest_framework import status
from functools import wraps
import logging
import traceback

# Configure logging
logger = logging.getLogger(__name__)

class ParkingException(Exception):
    """Base exception class for PerfectParking"""
    def __init__(self, message, code=None, details=None):
        super().__init__(message)
        self.message = message
        self.code = code or 'PARKING_ERROR'
        self.details = details or {}

class BookingError(ParkingException):
    """Booking related errors"""
    pass

class PaymentError(ParkingException):
    """Payment related errors"""
    pass

class ValidationError(ParkingException):
    """Data validation errors"""
    pass

class AuthenticationError(ParkingException):
    """Authentication related errors"""
    pass

def handle_exceptions(view_func):
    """Decorator for handling exceptions in views"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except ParkingException as e:
            logger.warning(f"Parking error: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': {
                    'code': e.code,
                    'message': e.message,
                    'details': e.details
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'An unexpected error occurred',
                    'reference': generate_error_reference()
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper

def generate_error_reference():
    """Generate unique reference for error tracking"""
    import uuid
    return str(uuid.uuid4())

class ErrorHandler:
    @staticmethod
    def log_error(error, context=None):
        """Log error with context"""
        error_data = {
            'error_type': type(error).__name__,
            'message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        logger.error(f"Application error: {error_data}")
        return error_data

    @staticmethod
    def format_api_error(error, include_details=False):
        """Format error for API response"""
        response = {
            'error': {
                'code': getattr(error, 'code', 'UNKNOWN_ERROR'),
                'message': str(error)
            }
        }
        
        if include_details and hasattr(error, 'details'):
            response['error']['details'] = error.details
            
        return response

class ValidationHandler:
    @staticmethod
    def validate_booking_data(data):
        """Validate booking data"""
        errors = {}
        
        if not data.get('start_time'):
            errors['start_time'] = 'Start time is required'
            
        if not data.get('duration'):
            errors['duration'] = 'Duration is required'
        elif not isinstance(data['duration'], (int, float)) or data['duration'] <= 0:
            errors['duration'] = 'Duration must be a positive number'
            
        if errors:
            raise ValidationError('Invalid booking data', details=errors)

    @staticmethod
    def validate_payment_data(data):
        """Validate payment data"""
        errors = {}
        
        if not data.get('amount'):
            errors['amount'] = 'Amount is required'
        elif not isinstance(data['amount'], (int, float)) or data['amount'] <= 0:
            errors['amount'] = 'Amount must be a positive number'
            
        if not data.get('payment_method'):
            errors['payment_method'] = 'Payment method is required'
            
        if errors:
            raise ValidationError('Invalid payment data', details=errors) 