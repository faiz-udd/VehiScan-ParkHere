from django.urls import re_path
from . import consumers

# Define websocket URL patterns
websocket_urlpatterns = [
    re_path(
        r'ws/parking-lot/(?P<parking_lot_id>\w+)/$',
        consumers.ParkingLotConsumer.as_asgi()
    ),
    re_path(
        r'ws/booking/(?P<booking_id>\w+)/$',
        consumers.BookingConsumer.as_asgi()
    ),
    re_path(
        r'ws/notifications/(?P<user_id>\w+)/$',
        consumers.NotificationConsumer.as_asgi()
    ),
]

# Define URL patterns for Django URLs
urlpatterns = []  # Empty list for Django URL patterns 