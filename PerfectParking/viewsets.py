from django.contrib.auth.models import User, Group
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from .serializers import UserProfileSerializer, GroupSerializer, ParkingLotSerializer, ParkingLotMonitorSerializer
from .models import ParkingLot, ParkingLotMonitor, ParkingSpot, Booking, Payment, UserProfile, Notification
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import ParkingSpotSerializer, BookingSerializer, PaymentSerializer, NotificationSerializer

class UserViewSet(ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        user = self.get_object()
        profile = UserProfile.objects.get(user=user)
        return Response(UserProfileSerializer(profile).data)

class GroupViewSet(ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class ParkingLotViewSet(ModelViewSet):
    """
    API endpoint that allows parking lots to be viewed or edited.
    """
    queryset = ParkingLot.objects.all()
    serializer_class = ParkingLotSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'])
    def available_spots(self, request, pk=None):
        parking_lot = self.get_object()
        spots = ParkingSpot.objects.filter(
            parking_lot=parking_lot,
            is_occupied=False
        )
        return Response(ParkingSpotSerializer(spots, many=True).data)

    @action(detail=True, methods=['post'])
    def update_occupancy(self, request, pk=None):
        parking_lot = self.get_object()
        try:
            parking_lot.current_occupancy = int(request.data.get('occupancy', 0))
            parking_lot.save()
            return Response({'status': 'success'})
        except ValueError:
            return Response(
                {'error': 'Invalid occupancy value'},
                status=status.HTTP_400_BAD_REQUEST
            )

class ParkingLotMonitorViewSet(ModelViewSet):
    """
    API endpoint that allows parking lot monitors to be viewed or edited.
    """
    queryset = ParkingLotMonitor.objects.all()
    serializer_class = ParkingLotMonitorSerializer
    #permission_classes = [permissions.IsAuthenticated]

class ParkingSpotViewSet(ModelViewSet):
    queryset = ParkingSpot.objects.all()
    serializer_class = ParkingSpotSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def toggle_occupancy(self, request, pk=None):
        spot = self.get_object()
        spot.is_occupied = not spot.is_occupied
        spot.save()
        return Response({'status': 'success'})

class BookingViewSet(ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status == 'PENDING':
            booking.status = 'CANCELLED'
            booking.cancellation_reason = request.data.get('reason', '')
            booking.save()
            return Response({'status': 'success'})
        return Response(
            {'error': 'Cannot cancel this booking'},
            status=status.HTTP_400_BAD_REQUEST
        )

# class PaymentViewSet(ModelViewSet):
#     serializer_class = PaymentSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return Payment.objects.filter(user=self.request.user)

class NotificationViewSet(ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({'status': 'success'})