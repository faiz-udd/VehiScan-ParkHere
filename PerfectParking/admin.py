from django.contrib import admin

from PerfectParking.models import ParkingLot, ParkingLotMonitor,  UserProfile

# Register your models here.

admin.site.register(ParkingLot)
admin.site.register(ParkingLotMonitor)
admin.site.register(UserProfile)