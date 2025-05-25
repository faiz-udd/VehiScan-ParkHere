from prometheus_client import Counter, Histogram, Gauge
from functools import wraps
import time
import psutil
import os

# Request metrics
REQUEST_LATENCY = Histogram(
    'request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

REQUEST_COUNT = Counter(
    'request_count_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

# Business metrics
BOOKING_COUNT = Counter(
    'booking_count_total',
    'Total number of bookings',
    ['status']
)

PARKING_OCCUPANCY = Gauge(
    'parking_lot_occupancy_ratio',
    'Current parking lot occupancy ratio',
    ['parking_lot_id']
)

PAYMENT_AMOUNT = Counter(
    'payment_amount_total',
    'Total payment amount',
    ['payment_method']
)

# System metrics
SYSTEM_MEMORY = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes'
)

CPU_USAGE = Gauge(
    'system_cpu_usage_ratio',
    'System CPU usage ratio'
)

class MetricsCollector:
    @staticmethod
    def collect_system_metrics():
        """Collect system metrics"""
        # Memory metrics
        memory = psutil.virtual_memory()
        SYSTEM_MEMORY.set(memory.used)

        # CPU metrics
        CPU_USAGE.set(psutil.cpu_percent(interval=1) / 100.0)

    @staticmethod
    def track_request(method, endpoint, status_code, duration):
        """Track request metrics"""
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status=status_code
        ).inc()

        REQUEST_LATENCY.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

    @staticmethod
    def track_booking(status):
        """Track booking metrics"""
        BOOKING_COUNT.labels(status=status).inc()

    @staticmethod
    def update_parking_occupancy(parking_lot_id, ratio):
        """Update parking lot occupancy"""
        PARKING_OCCUPANCY.labels(
            parking_lot_id=parking_lot_id
        ).set(ratio)

    @staticmethod
    def track_payment(amount, method):
        """Track payment metrics"""
        PAYMENT_AMOUNT.labels(
            payment_method=method
        ).inc(amount)

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time

        # Record metrics
        REQUEST_LATENCY.labels(
            method=func.__name__,
            endpoint='internal'
        ).observe(duration)

        return result
    return wrapper 