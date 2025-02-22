from django.core.management.base import BaseCommand
from PerfectParking.models import ParkingLot
from decimal import Decimal

class Command(BaseCommand):
    help = 'Creates initial parking lot data'

    def handle(self, *args, **kwargs):
        # Create some sample parking lots with all required fields
        ParkingLot.objects.create(
            name="Central Parking",
            address="123 Main St",
            total_spaces=100,
            available_spaces=100,
            latitude=40.7128,
            longitude=-74.0060,
            base_price_per_hour=Decimal('5.00'),
            surge_multiplier=Decimal('1.00'),
            has_ai_detection=False
        )
        
        ParkingLot.objects.create(
            name="Downtown Parking",
            address="456 Oak Ave",
            total_spaces=50,
            available_spaces=50,
            latitude=34.0522,
            longitude=-118.2437,
            base_price_per_hour=Decimal('7.50'),
            surge_multiplier=Decimal('1.00'),
            has_ai_detection=False
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully created initial data'))