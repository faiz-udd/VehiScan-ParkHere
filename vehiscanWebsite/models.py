from geopy.distance import geodesic
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

# User Schema

class UserType(models.TextChoices):
    DRIVER = 'driver', _('Driver')
    LOT_OWNER = 'lot_owner', _('Parking Lot Owner')
    ADMIN = 'admin', _('Administrator')

#User Profile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)  # Changed from avatar_url
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.DRIVER
    )
    phone_number = models.CharField(max_length=20, blank=True)
    #fields related to Driver
    vehicle_type = models.CharField(max_length=20, blank=True)
    license_plate = models.CharField(max_length=15, blank=True)
    
    #fields related to Parking Lot Owner
    company_name = models.CharField(max_length=255, blank=True)
    stripe_account_id = models.CharField(max_length=100, blank=True)  # For payment processing
    

    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"

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
    base_price_per_hour = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'))
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='owned_lots',
        limit_choices_to={'user_type': UserType.LOT_OWNER}
    )
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=Decimal('10.00'),
        validators=[MinValueValidator(0)]
    )

    def get_image_url(self):
        if self.image:
            return self.image.url
        return ''

    def calculate_distance(self, user_latitude, user_longitude):
        return geodesic((self.latitude, self.longitude), (user_latitude, user_longitude)).km

    def get_free_parking_spaces(self):
        monitor = ParkingLotMonitor.objects.filter(parkingLot=self).first()
        if monitor:
            return monitor.free_parking_spaces
        return 0

    def get_probability_parking_available(self):
        monitor = ParkingLotMonitor.objects.filter(parkingLot=self).first()
        if monitor:
            return int(((monitor.free_parking_spaces)/(self.parking_spaces))*100)
        return 0

    def get_date_time_last_updated(self):
        monitor = ParkingLotMonitor.objects.filter(parkingLot=self).first()
        if monitor:
            return monitor.dateTimeLastUpdated
        return None

    def __str__(self) -> str:
        return str(self.name)


class ParkingLotMonitor(models.Model):
  
    id = models.AutoField(primary_key=True)
    parkingLot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    latitude = models.DecimalField(max_digits=17, decimal_places=15)
    longitude = models.DecimalField(max_digits=17, decimal_places=15)
    probabilityParkingAvailable = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.00') )
    free_parking_spaces = models.IntegerField(default=0)
    total_parking_spaces = models.IntegerField(default=0)
    dateTimeLastUpdated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    image = models.ImageField(upload_to="images/parking-lot-monitor/", blank=True)
    camera_stream_url = models.URLField(blank=True)
    detection_confidence = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    def update_availability(self, new_count, confidence):
        self.free_parking_spaces = new_count
        self.detection_confidence = confidence
        self.save()
        ParkingLotLog.objects.create(
            parking_lot=self.parkingLot,
            free_parking_spaces=new_count,
            confidence=confidence
        )
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
    """The latitude of the parking lot monitor"""
    area_of_interest_longitude = models.DecimalField(max_digits=17, decimal_places=15)
    time_stamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    user_ip_address = models.CharField(max_length=15)
    
# this is used to log the parking request made by the user