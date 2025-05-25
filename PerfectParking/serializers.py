# from django.contrib.auth.models import User, Group
# from rest_framework import serializers
# from .models import ParkingLot, ParkingLotMonitor

# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     """
#     A serializer for the User model.

#     Attributes:
#         None.

#     Methods:
#         None.
#     """
#     class Meta:
#         model = User
#         fields = ['url', 'username', 'email', 'groups']


# class GroupSerializer(serializers.HyperlinkedModelSerializer):
#     """ this is a serializer for the Group model

#     Args:
#         serializers (_type_): the type of serializer
#     """
#     class Meta:
#         model = Group
#         fields = ['url', 'name']
        
# class ParkingLotSerializer(serializers.HyperlinkedModelSerializer):
#     """ this is a serializer for the ParkingLot model
#     """
#     class Meta:
#         model = ParkingLot
#         fields = ['id', 'name', 'latitude', 'longitude']

# class ParkingLotMonitorSerializer(serializers.HyperlinkedModelSerializer):
#     """this is a serializer for the ParkingLotMonitor model

#     Args:
#         serializers (_type_): the type of serializer
#     """
#     class Meta:
#         """this is a serializer for the ParkingLotMonitor model
#         """
#         model = ParkingLotMonitor
#         fields = ['id', 'name', 'latitude', 'longitude', 'probabilityParkingAvailable']





# from rest_framework import serializers
# from .models import (
#     ParkingLotOwner, ParkingLot, ParkingLotMonitor, ParkingLotLog,
#     ParkingRequestLog, ParkingSpot, Booking, UserProfile, Payment, Notification
# )

# class ParkingLotOwnerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ParkingLotOwner
#         fields = ['id', 'user', 'company_name', 'subscription_plan', 'stripe_customer_id']

# class ParkingLotSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ParkingLot
#         fields = [
#             'id', 'name', 'address', 'total_spaces', 'available_spaces', 'hours',
#             'isPaidParking', 'latitude', 'longitude', 'image', 'parking_spaces',
#             'owner', 'base_price_per_hour', 'surge_multiplier', 'has_ai_detection',
#             'camera_stream_url'
#         ]

# class ParkingLotMonitorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ParkingLotMonitor
#         fields = [
#             'id', 'parkingLot', 'name', 'latitude', 'longitude',
#             'probabilityParkingAvailable', 'free_parking_spaces',
#             'dateTimeLastUpdated', 'status', 'image'
#         ]

# class ParkingLotLogSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ParkingLotLog
#         fields = ['id', 'parking_lot', 'logged_by_monitor', 'free_parking_spaces', 'time_stamp']

# class ParkingRequestLogSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ParkingRequestLog
#         fields = [
#             'id', 'area_of_interest_latitude', 'area_of_interest_longitude',
#             'time_stamp', 'user', 'user_ip_address'
#         ]

# class ParkingSpotSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ParkingSpot
#         fields = ['id', 'parking_lot', 'spot_number', 'is_occupied', 'last_detection_time']

# class BookingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Booking
#         fields = [
#             'id', 'user', 'parking_spot', 'start_time', 'end_time',
#             'total_cost', 'stripe_payment_id', 'status', 'qr_code'
#         ]

# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserProfile
#         fields = [
#             'id', 'user', 'role', 'phone_number', 'preferred_payment_method',
#             'notification_settings'
#         ]

# class PaymentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Payment
#         fields = ['id', 'user', 'booking', 'amount', 'status', 'created_at', 'updated_at']

# class NotificationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Notification
#         fields = ['id', 'user', 'message', 'created_at', 'read']




from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import (
    ParkingLotOwner, ParkingLot, ParkingLotMonitor, ParkingLotLog,
    ParkingRequestLog, ParkingSpot, Booking, UserProfile, Payment, Notification
)

class ParkingLotOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLotOwner
        fields = ['id', 'user', 'company_name', 'subscription_plan', 'stripe_customer_id']

class ParkingLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLot
        fields = [
            'id', 'name', 'address', 'total_spaces', 'available_spaces', 'hours',
            'isPaidParking', 'latitude', 'longitude', 'image', 'parking_spaces',
            'owner', 'base_price_per_hour', 'surge_multiplier', 'has_ai_detection',
            'camera_stream_url'
        ]

class ParkingLotMonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLotMonitor
        fields = [
            'id', 'parkingLot', 'name', 'latitude', 'longitude',
            'probabilityParkingAvailable', 'free_parking_spaces',
            'dateTimeLastUpdated', 'status', 'image'
        ]

class ParkingLotLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLotLog
        fields = ['id', 'parking_lot', 'logged_by_monitor', 'free_parking_spaces', 'time_stamp']

class ParkingRequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingRequestLog
        fields = [
            'id', 'area_of_interest_latitude', 'area_of_interest_longitude',
            'time_stamp', 'user', 'user_ip_address'
        ]

class ParkingSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSpot
        fields = ['id', 'parking_lot', 'spot_number', 'is_occupied', 'last_detection_time']

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'parking_spot', 'start_time', 'end_time',
            'total_cost', 'stripe_payment_id', 'status', 'qr_code'
        ]

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'role', 'phone_number', 'preferred_payment_method',
            'notification_settings'
        ]

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'booking', 'amount', 'status', 'created_at', 'updated_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at', 'read']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    """ this is a serializer for the Group model

    Args:
        serializers (_type_): the type of serializer
    """
    class Meta:
        model = Group
        fields = ['url', 'name']