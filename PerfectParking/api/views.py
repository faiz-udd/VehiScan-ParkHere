from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
import stripe
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import ParkingLot, ParkingSpot, Booking, Notification, Payment  # Note: Using Booking instead of ParkingBooking
from ..serializers import (
    ParkingLotSerializer,
    ParkingSpotSerializer,
    BookingSerializer,
    UserProfileSerializer,
    NotificationSerializer,
    PaymentSerializer
)
from ..services import BookingService, PaymentService
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.core.exceptions import ValidationError
from django.db import connection
from django.db import reset_queries
import time

stripe.api_key = settings.STRIPE_SECRET_KEY

class ParkingLotViewSet(viewsets.ModelViewSet):
    queryset = ParkingLot.objects.all()
    serializer_class = ParkingLotSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    @swagger_auto_schema(
        method='get',
        operation_description="Get available parking spaces",
        responses={
            200: openapi.Response(
                description="Available spaces",
                schema=ParkingLotSerializer
            )
        }
    )
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        try:
            parking_lot = self.get_object()
            return Response({
                'total_spaces': parking_lot.total_spaces,
                'available_spaces': parking_lot.available_spaces,
                'occupied_spaces': parking_lot.total_spaces - parking_lot.available_spaces
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        method='post',
        operation_description="Reserve a parking space",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'start_time': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                'duration': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        )
    )
    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        parking_lot = self.get_object()
        try:
            booking = BookingService.create_booking(
                user=request.user,
                parking_lot=parking_lot,
                start_time=request.data['start_time'],
                duration=request.data['duration']
            )
            return Response(BookingSerializer(booking).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        qs = super().get_queryset()
        if settings.DEBUG:
            reset_queries()
            start_time = time.time()
            result = list(qs)
            end_time = time.time()
            
            # Log query information
            for query in connection.queries:
                print(f"SQL Query: {query['sql']}")
                print(f"Time: {query['time']}s")
            
            print(f"Total queries: {len(connection.queries)}")
            print(f"Total time: {end_time - start_time:.2f}s")
            
            return result
        return qs

class ParkingSpotViewSet(viewsets.ModelViewSet):
    """API endpoint for managing parking spots"""
    
    @action(detail=True, methods=['post'])
    def update_occupancy(self, request, pk=None):
        """Update spot occupancy from AI detection"""
        spot = self.get_object()
        is_occupied = request.data.get('is_occupied', False)
        spot.is_occupied = is_occupied
        spot.save()
        
        # Broadcast update to connected clients
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"parking_lot_{spot.parking_lot.id}",
            {
                "type": "spot_update",
                "spot_id": spot.id,
                "is_occupied": is_occupied
            }
        )
        return Response({'status': 'updated'})

    @action(detail=True, methods=['post'])
    def book_spot(self, request, pk=None):
        try:
            spot = self.get_object()
            if spot.is_occupied:
                raise ValidationError('Spot already occupied')

            booking = BookingService.create_booking(
                user=request.user,
                parking_spot=spot,
                start_time=request.data.get('start_time'),
                duration=request.data.get('duration')
            )

            payment_intent = PaymentService.create_payment_intent(
                booking=booking,
                user=request.user
            )

            return Response({
                'booking_id': booking.id,
                'client_secret': payment_intent.client_secret
            })

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MobileAppViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['device_token', 'platform'],
            properties={
                'device_token': openapi.Schema(type=openapi.TYPE_STRING),
                'platform': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['ios', 'android']
                ),
            }
        )
    )
    @action(detail=False, methods=['post'])
    def register_device(self, request):
        try:
            device_token = request.data.get('device_token')
            platform = request.data.get('platform')

            if not device_token or platform not in ['ios', 'android']:
                raise ValidationError('Invalid device token or platform')

            # Store device information in user profile
            user_profile = request.user.userprofile
            user_profile.device_token = device_token
            user_profile.device_platform = platform
            user_profile.save()

            return Response({'status': 'Device registered successfully'})

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        try:
            BookingService.cancel_booking(booking)
            return Response({'status': 'booking cancelled'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def extend(self, request, pk=None):
        booking = self.get_object()
        try:
            extended_booking = BookingService.extend_booking(
                booking=booking,
                additional_hours=request.data.get('hours', 1)
            )
            return Response(BookingSerializer(extended_booking).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'all marked as read'})

class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing payments
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        payment = self.get_object()
        try:
            # Add payment processing logic here
            payment.status = 'COMPLETED'
            payment.save()
            return Response({'status': 'success'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        payment = self.get_object()
        if payment.status == 'PENDING':
            payment.status = 'CANCELLED'
            payment.save()
            return Response({'status': 'success'})
        return Response(
            {'error': 'Cannot cancel this payment'},
            status=status.HTTP_400_BAD_REQUEST
        )