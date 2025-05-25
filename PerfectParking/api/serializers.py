from rest_framework import serializers
from ..models import (
    ParkingLot,
    ParkingSpot,
    Booking,
    Notification,
    UserProfile
)

class ParkingLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLot
        fields = [
            'id', 'name', 'address', 'total_spaces',
            'available_spaces', 'hourly_rate', 'latitude', 'longitude'
        ]

class ParkingSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSpot
        fields = ['id', 'spot_number', 'is_occupied', 'parking_lot']

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'parking_spot', 'start_time',
            'end_time', 'total_cost', 'status'
        ]
        read_only_fields = ['user', 'total_cost', 'status']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at']
        read_only_fields = ['user']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'phone_number', 'preferred_payment_method']
        read_only_fields = ['user'] 