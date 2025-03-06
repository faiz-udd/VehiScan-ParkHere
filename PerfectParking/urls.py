""" PerfectParking URL Configuration"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from . import views
from .api.views import (
    ParkingLotViewSet,
    BookingViewSet,
    ParkingSpotViewSet,
    PaymentViewSet,
    NotificationViewSet,
    MobileAppViewSet
)
# from .admin.views import admin_dashboard
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings


app_name = 'PerfectParking'

# API Documentation Schema
schema_view = get_schema_view(
    openapi.Info(
        title="Perfect Parking API",
        default_version='v1',
        description="API documentation for Perfect Parking System",
        contact=openapi.Contact(email="contact@perfectparking.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# API Router
router = DefaultRouter()
router.register(r'parking-lots', ParkingLotViewSet, basename='parking-lot')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'parking-spots', ParkingSpotViewSet, basename='parking-spot')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'mobile', MobileAppViewSet, basename='mobile')

urlpatterns = [
    # Web Interface URLs
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register-user'),
    
    # Parking Lot Management
    path('parking-lots/', views.parking_lots, name='parking-lots'),
    path('parking-lots/<int:pk>/', views.parking_lot_detail, name='parking-lot-detail'),
    path('parking-lots/nearby/', views.nearby_parking_lots, name='nearby-parking-lots'),
    
    # Booking Management
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking-detail'),
    path('bookings/<int:pk>/cancel/', views.cancel_booking, name='cancel-booking'),
    path('booking-history/', views.booking_history, name='booking-history'),
    
    # User Profile and Payment
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile, name='update-profile'),
    path('profile/payment/add/', views.add_payment_method, name='add_payment_method'),
    
    # Monitor Management
    path('monitors/', views.parking_lot_monitors, name='parking-lot-monitors'),
    path('monitors/<int:id>/', views.parking_lot_monitor, name='parking-lot-details'),
    path('monitors/status/', views.monitor_status, name='monitor-status'),
    
    # Admin Dashboard
    #path('admin/dashboard/', admin_dashboard, name='admin-dashboard'),
    
    # API URLs
    path('api/', include((router.urls, 'api'), namespace='api')),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Static Pages
    path('privacy-policy/', TemplateView.as_view(
        template_name='website/privacy-policy.html'
    ), name='privacy-policy'),
    path('terms/', TemplateView.as_view(
        template_name='website/terms.html'
    ), name='terms'),
]

# Error handlers
handler404 = 'PerfectParking.views.error_404'
handler500 = 'PerfectParking.views.error_500'
handler403 = 'PerfectParking.views.error_403'
handler400 = 'PerfectParking.views.error_400'
