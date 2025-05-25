
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from ..models import ParkingLot, Booking, Payment
from ..error_handling import BookingError, PaymentError
import datetime

class ParkingLotTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.parking_lot = ParkingLot.objects.create(
            name='Test Parking',
            address='123 Test St',
            total_spaces=100,
            hourly_rate=10.00
        )

    def test_available_spaces(self):
        """Test available spaces calculation"""
        # Create active bookings
        start_time = timezone.now()
        end_time = start_time + datetime.timedelta(hours=2)
        
        Booking.objects.create(
            user=self.user,
            parking_lot=self.parking_lot,
            start_time=start_time,
            end_time=end_time
        )
        
        self.assertEqual(self.parking_lot.available_spaces, 99)

    def test_is_full(self):
        """Test parking lot full status"""
        # Book all spaces
        start_time = timezone.now()
        end_time = start_time + datetime.timedelta(hours=2)
        
        for _ in range(100):
            Booking.objects.create(
                user=self.user,
                parking_lot=self.parking_lot,
                start_time=start_time,
                end_time=end_time
            )
            
        self.assertTrue(self.parking_lot.is_full())

class BookingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.parking_lot = ParkingLot.objects.create(
            name='Test Parking',
            total_spaces=100,
            hourly_rate=10.00
        )

    def test_create_booking(self):
        """Test booking creation"""
        start_time = timezone.now()
        end_time = start_time + datetime.timedelta(hours=2)
        
        booking = Booking.objects.create(
            user=self.user,
            parking_lot=self.parking_lot,
            start_time=start_time,
            end_time=end_time
        )
        
        self.assertEqual(booking.calculate_total(), 20.00)
        self.assertEqual(booking.duration_hours(), 2)

    def test_overlapping_bookings(self):
        """Test overlapping bookings prevention"""
        start_time = timezone.now()
        end_time = start_time + datetime.timedelta(hours=2)
        
        # Create first booking
        Booking.objects.create(
            user=self.user,
            parking_lot=self.parking_lot,
            start_time=start_time,
            end_time=end_time
        )
        
        # Attempt to create overlapping booking
        with self.assertRaises(BookingError):
            Booking.objects.create(
                user=self.user,
                parking_lot=self.parking_lot,
                start_time=start_time + datetime.timedelta(hours=1),
                end_time=end_time + datetime.timedelta(hours=1)
            ) 