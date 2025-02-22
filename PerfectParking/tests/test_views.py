
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import ParkingLot, Booking
from rest_framework import status
import json

class ParkingLotViewTests(TestCase):
    def setUp(self):
        self.client = Client()
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
        self.client.login(username='testuser', password='testpass123')

    def test_parking_lot_list(self):
        """Test parking lot listing"""
        response = self.client.get(reverse('parking_lots'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'website/parking-lots.html')

    def test_parking_lot_detail(self):
        """Test parking lot detail view"""
        response = self.client.get(
            reverse('parking_lot_detail', kwargs={'pk': self.parking_lot.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'website/parking-lot.html')

    def test_parking_lot_search(self):
        """Test parking lot search functionality"""
        response = self.client.get(
            reverse('parking_lots'),
            {'query': 'Test Parking'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Test Parking')

class BookingViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.parking_lot = ParkingLot.objects.create(
            name='Test Parking',
            total_spaces=100,
            hourly_rate=10.00
        )
        self.client.login(username='testuser', password='testpass123')

    def test_create_booking(self):
        """Test booking creation"""
        response = self.client.post(
            reverse('create_booking'),
            {
                'parking_lot': self.parking_lot.pk,
                'start_time': '2024-03-20T10:00:00Z',
                'duration': 2
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Booking.objects.exists())

    def test_cancel_booking(self):
        """Test booking cancellation"""
        booking = Booking.objects.create(
            user=self.user,
            parking_lot=self.parking_lot,
            start_time='2024-03-20T10:00:00Z',
            end_time='2024-03-20T12:00:00Z'
        )
        
        response = self.client.post(
            reverse('cancel_booking', kwargs={'pk': booking.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'CANCELLED') 