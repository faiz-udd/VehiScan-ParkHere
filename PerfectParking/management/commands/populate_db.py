from django.core.management.base import BaseCommand
from PerfectParking.models import ParkingLot, ParkingLotMonitor
from decimal import Decimal, InvalidOperation
import subprocess
import os

class Command(BaseCommand):
    help = 'Creates initial parking lot data'

    def handle(self, *args, **kwargs):
        try:
            # Create some sample parking lots with all required fields
            parking_lot_1 = ParkingLot.objects.create(
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
            
            parking_lot_2 = ParkingLot.objects.create(
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

            # Create some sample parking lot monitors
            if not ParkingLotMonitor.objects.filter(name="Monitor 1").exists():
                ParkingLotMonitor.objects.create(
                    parkingLot=parking_lot_1,
                    name="Monitor 1",
                    latitude=Decimal('40.7128'),
                    longitude=Decimal('-74.0060'),
                    probabilityParkingAvailable=Decimal('0.75'),
                    free_parking_spaces=75,
                    status=True
                )

            if not ParkingLotMonitor.objects.filter(name="Monitor 2").exists():
                ParkingLotMonitor.objects.create(
                    parkingLot=parking_lot_2,
                    name="Monitor 2",
                    latitude=Decimal('34.0522'),
                    longitude=Decimal('-118.2437'),
                    probabilityParkingAvailable=Decimal('0.50'),
                    free_parking_spaces=25,
                    status=True
                )

            self.stdout.write(self.style.SUCCESS('Successfully created initial data'))
        except InvalidOperation as e:
            self.stdout.write(self.style.ERROR(f'Error creating initial data: {e}'))