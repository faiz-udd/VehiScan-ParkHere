from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .docs import schema_view

router = DefaultRouter()
router.register(r'parking-lots', views.ParkingLotViewSet)
router.register(r'bookings', views.BookingViewSet)
router.register(r'parking-spots', views.ParkingSpotViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'notifications', views.NotificationViewSet)
router.register(r'mobile', views.MobileAppViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] 