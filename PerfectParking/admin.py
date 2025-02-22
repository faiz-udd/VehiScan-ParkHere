from django.contrib import admin
from .models import ParkingLot, ParkingLotMonitor, ParkingSpot, Booking, UserProfile, Payment, Notification

admin.site.register(ParkingLot)
admin.site.register(ParkingLotMonitor)

@admin.register(ParkingLot)
class ParkingLotAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'total_spaces', 'available_spaces', 'base_price_per_hour')
    search_fields = ('name', 'address')

@admin.register(ParkingLotMonitor)
class ParkingLotMonitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'parkingLot', 'latitude', 'longitude', 'status')
    search_fields = ('name', 'parkingLot__name')

@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ('parking_lot', 'spot_number', 'is_occupied')
    search_fields = ('parking_lot__name', 'spot_number')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'parking_spot', 'start_time', 'end_time', 'total_cost', 'status')
    search_fields = ('user__username', 'parking_spot__spot_number')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone_number')
    search_fields = ('user__username', 'role')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'booking', 'amount', 'status', 'created_at')
    search_fields = ('user__username', 'booking__id')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'read')
    search_fields = ('user__username', 'message')