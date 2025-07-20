from django.contrib import admin

from vehiscanWebsite.models import ParkingLot, ParkingLotMonitor,  UserProfile, EmailOTP

# Register your models here.

admin.site.register(ParkingLot)
admin.site.register(ParkingLotMonitor)
admin.site.register(UserProfile)
admin.site.register(EmailOTP)