#Description: This file contains the models for the website.
from geopy.distance import geodesic
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ParkingLot(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255)
    hours = models.CharField(max_length=255)
    isPaidParking = models.BooleanField(default=True)
    latitude = models.DecimalField(max_digits=17, decimal_places=15)
    longitude = models.DecimalField(max_digits=17, decimal_places=15)
    image = models.ImageField(upload_to="images/parking-lot/", blank=True)
    parking_spaces = models.IntegerField(default=1)
    
    def __str__(self) -> str:
        return str(self.name)


class ParkingLotMonitor(models.Model):
    
    id = models.AutoField(primary_key=True)
    parkingLot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    latitude = models.DecimalField(max_digits=17, decimal_places=15)
    longitude = models.DecimalField(max_digits=17, decimal_places=15)
    probabilityParkingAvailable = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0
    )
    free_parking_spaces = models.IntegerField(default=0)
    dateTimeLastUpdated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    image = models.ImageField(upload_to="images/parking-lot-monitor/", blank=True)


    def get_occupancy_rate(self) -> int:
        return round(100 - self.probabilityParkingAvailable * 100)

    def get_vacancy_rate(self) -> int:
        return round(self.probabilityParkingAvailable * 100)

    def get_distance_from_lat_lang(self, latitude, longitude) -> float:
        point: tuple = (latitude, longitude)
        return self.get_distance_from_point(point)

    def get_distance_from_point(self, user_point: tuple) -> float:
        return round(geodesic(self.get_gps_point(), user_point).km, 2)

    def get_gps_point(self) -> tuple:
        return (self.latitude, self.longitude)

    def __str__(self) -> str:
        return str(self.name)

    def update(self, *args, **kwargs):
        super(ParkingLotMonitor, self).save(*args, **kwargs)
        ParkingLotLog.objects.create(parking_lot=self.parkingLot, logged_by_monitor=self, free_parking_spaces=self.free_parking_spaces)

    def save(self, *args, **kwargs):
        super(ParkingLotMonitor, self).save(*args, **kwargs)
        ParkingLotLog.objects.create(parking_lot=self.parkingLot, logged_by_monitor=self, free_parking_spaces=self.free_parking_spaces)


class ParkingLotLog(models.Model):
    id = models.AutoField(primary_key=True)
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    logged_by_monitor = models.ForeignKey(ParkingLotMonitor, on_delete=models.CASCADE)
    free_parking_spaces = models.IntegerField(default=0)
    time_stamp = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.parking_lot.name} - {self.time_stamp}"


class ParkingRequestLog(models.Model):

    id = models.AutoField(primary_key=True)
    area_of_interest_latitude = models.DecimalField(max_digits=17, decimal_places=15)
    area_of_interest_longitude = models.DecimalField(max_digits=17, decimal_places=15)
    time_stamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    user_ip_address = models.CharField(max_length=15)