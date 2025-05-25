"""Defines the models used in the PerfectParking app."""
from geopy.distance import geodesic
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

# Create your models here.
class ParkingLotOwner(models.Model):
    """Model for parking lot owners/businesses"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    subscription_plan = models.CharField(
        max_length=20,
        choices=[
            ('FREE', 'Free Plan'),
            ('BASIC', 'Basic Plan'),
            ('PRO', 'Pro Plan'),
            ('ENTERPRISE', 'Enterprise Plan')
        ],
        default='FREE'
    )
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.company_name

class ParkingLot(models.Model):
    """
    A model representing a parking lot.

    Attributes:
        id (int): The primary key of the parking lot.
        name (str): The name of the parking lot (max length 100).
        address (str): The address of the parking lot (max length 255).
        hours (str): The operating hours of the parking lot (max length 255).
        isPaidParking (bool): Whether the parking lot requires payment or not (default True).
        latitude (Decimal): The latitude of the parking lot location (max digits 17, decimal places 15).
        longitude (Decimal): The longitude of the parking lot location (max digits 17, decimal places 15).
        image (ImageField): An optional image of the parking lot (uploaded to 'images/parking-lot/').
        parking_spaces (int): The number of parking spaces available (default 1).
        owner (ForeignKey): A foreign key to the ParkingLotOwner that this parking lot belongs to.
        base_price_per_hour (Decimal): The base price per hour for parking (max digits 6, decimal places 2).
        surge_multiplier (Decimal): The surge multiplier for pricing (max digits 3, decimal places 2, default 1.00).
        has_ai_detection (bool): Whether the parking lot has AI detection (default False).
        camera_stream_url (URLField): An optional URL for the camera stream (max length 200).
        max_capacity (int): The maximum capacity of the parking lot (default 0).
        current_occupancy (int): The current occupancy of the parking lot (default 0).
        operating_hours (JSONField): Store hours for each day (default dict).
        amenities (JSONField): List of available amenities (default list).
        is_active (bool): Whether the parking lot is active (default True).
        last_updated (DateTimeField): The date and time when the parking lot was last updated (auto_now=True).

    Methods:
        __str__(): Returns the name of the parking lot as a string.
        get_current_price(): Calculates the current price including surge pricing.
        get_occupancy_percentage(): Calculate current occupancy percentage.
        is_full(): Check if parking lot is at capacity.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    total_spaces = models.IntegerField()
    available_spaces = models.IntegerField()
    hours = models.CharField(max_length=255)
    isPaidParking = models.BooleanField(default=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to='parking_lots/', null=True, blank=True)
    parking_spaces = models.IntegerField(default=1)
    owner = models.ForeignKey(
        'ParkingLotOwner', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='parking_lots'
    )
    base_price_per_hour = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        default=Decimal('0.00')
    )
    surge_multiplier = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        default=Decimal('1.00')
    )
    has_ai_detection = models.BooleanField(default=False)
    camera_stream_url = models.URLField(blank=True)
    max_capacity = models.IntegerField(default=0)
    current_occupancy = models.IntegerField(default=0)
    operating_hours = models.JSONField(default=dict)
    amenities = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_current_price(self):
        """Calculate current price including surge pricing"""
        return self.base_price_per_hour * self.surge_multiplier

    def get_image_url(self):
        """Return image URL or default image if none exists"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/default_parking.png'  # Create this default image

    def get_occupancy_percentage(self):
        """Calculate current occupancy percentage"""
        if self.max_capacity == 0:
            return 0
        return round((self.current_occupancy / self.max_capacity) * 100)
    
    def is_full(self):
        """Check if parking lot is at capacity"""
        return self.current_occupancy >= self.max_capacity

class ParkingLotMonitor(models.Model):
    """
    A model representing a parking lot monitor.

    Attributes:
        id (int): The primary key of the parking lot monitor.
        parkingLot (ForeignKey): A foreign key to the ParkingLot that this monitor is associated with.
        name (str): The name of the parking lot monitor (max length 100).
        latitude (Decimal): The latitude of the parking lot monitor location (max digits 17, decimal places 15).
        longitude (Decimal): The longitude of the parking lot monitor location (max digits 17, decimal places 15).
        probabilityParkingAvailable (Decimal): The probability that the parking lot is available (max digits 5, decimal places 2, default 0).
        free_parking_spaces (int): The number of free parking spaces available (default 0).
        dateTimeLastUpdated (DateTimeField): The date and time when the monitor was last updated (auto_now=True).
        status (bool): Whether the monitor is currently online or offline (default True).
        image (ImageField): An optional image of the parking lot monitor (uploaded to 'images/parking-lot-monitor/').
        last_maintenance (DateTimeField): The date and time when the last maintenance was performed (null=True, blank=True).
        maintenance_due (DateTimeField): The date and time when the next maintenance is due (null=True, blank=True).
        camera_status (CharField): The status of the camera (max length 20, choices=['ACTIVE', 'INACTIVE', 'MAINTENANCE'], default='ACTIVE').

    Methods:
        None.
    """

    id = models.AutoField(primary_key=True)
    parkingLot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    """The name of the parking lot monitor.
    This is the name that will be displayed to the user.
    Max length is 100 characters."""
    latitude = models.DecimalField(max_digits=17, decimal_places=15)
    """The latitude of the parking lot monitor"""
    longitude = models.DecimalField(max_digits=17, decimal_places=15)
    """The longitude of the parking lot monitor"""
    probabilityParkingAvailable = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.00')
    )
    """The probability that the parking lot is available."""
    free_parking_spaces = models.IntegerField(default=0)
    dateTimeLastUpdated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    """status: True = online, False = offline"""
    image = models.ImageField(upload_to="images/parking-lot-monitor/", blank=True)

    def get_image_url(self):
        """Return image URL or default image if none exists"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/no-camera.jpg'  # Default image


    def get_occupancy_rate(self) -> int:
        """Gets the occupancy % rate of the parking lot.

        Returns:
            int: The occupancy % rate of the parking lot.
        """
        return round(100 - self.probabilityParkingAvailable * 100)

    def get_vacancy_rate(self) -> int:
        """Gets the vacancy % rate of the parking lot.

        Returns:
            int: The vacancy % rate of the parking lot.
        """
        return round(self.probabilityParkingAvailable * 100)

    def get_distance_from_lat_lang(self, latitude, longitude) -> float:
        """Calculates the distance between the current object and a point specified by latitude and longitude.

        Args:
            latitude (float): The latitude of the point in degrees.
            longitude (float): The longitude of the point in degrees.

        Returns:
            float: The distance between the current object and the specified point in kilometers.

        Raises:
            None.
        """
        point: tuple = (latitude, longitude)
        return self.get_distance_from_point(point)

    def get_distance_from_point(self, user_point: tuple) -> float:
        """Gets the distance in Kilometers from the user GPS coordinates to the parking lot coordinates.

        Returns:
            float: The distance in Kilometers from the user GPS coordinates to the parking lot coordinates.
        """
        return round(geodesic(self.get_gps_point(), user_point).km, 2)

    def get_gps_point(self) -> tuple:
        """Gets the GPS coordinates of the parking lot.

        Returns:
            tuple: The GPS coordinates of the parking lot.
        """
        return (self.latitude, self.longitude)

    def __str__(self) -> str:
        return str(self.name)

    def update(self, *args, **kwargs):
        """Overrides the update method to create a parking lot log."""
        super(ParkingLotMonitor, self).save(*args, **kwargs)
        ParkingLotLog.objects.create(parking_lot=self.parkingLot, logged_by_monitor=self, free_parking_spaces=self.free_parking_spaces)

    def save(self, *args, **kwargs):
        """Overrides the save method to create a parking lot log."""
        super(ParkingLotMonitor, self).save(*args, **kwargs)
        ParkingLotLog.objects.create(parking_lot=self.parkingLot, logged_by_monitor=self, free_parking_spaces=self.free_parking_spaces)

class ParkingLotLog(models.Model):
    """
    A model representing a parking lot log. This model is used to store the history of parking lot monitor updates.
    The date-time, free parking spaces, and probability parking available are stored.

    Attributes:
        id (int): The primary key of the parking lot monitor.
        parking_lot (ForeignKey): A foreign key to the ParkingLot that this monitor is associated with.
        free_parking_spaces (int): The number of free parking spaces available (default 0).
        time_stamp (DateTimeField): The date and time when the monitor was last updated (auto_now=True).

    Methods:
        None.
    """

    id = models.AutoField(primary_key=True)
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    logged_by_monitor = models.ForeignKey(ParkingLotMonitor, on_delete=models.CASCADE)
    free_parking_spaces = models.IntegerField(default=0)
    time_stamp = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.parking_lot.name} - {self.time_stamp}"

class ParkingRequestLog(models.Model):
    """
    A model representing a parking request log. This model is used to store the history of parking requests.
    The date-time, user, user-location are stored.
    """

    id = models.AutoField(primary_key=True)
    area_of_interest_latitude = models.DecimalField(max_digits=17, decimal_places=15)
    """The latitude of the parking lot monitor"""
    area_of_interest_longitude = models.DecimalField(max_digits=17, decimal_places=15)
    time_stamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    user_ip_address = models.CharField(max_length=15)

class ParkingSpot(models.Model):
    """Individual parking spots within a lot"""
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    spot_number = models.CharField(max_length=10)
    is_occupied = models.BooleanField(default=False)
    last_detection_time = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['parking_lot', 'spot_number']

class Booking(models.Model):
    """Parking spot reservations"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)
    stripe_payment_id = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('CONFIRMED', 'Confirmed'),
            ('CHECKED_IN', 'Checked In'),
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled')
        ],
        default='PENDING'
    )
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    rating = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=[
            ('CUSTOMER', 'Customer'),
            ('LOT_OWNER', 'Parking Lot Owner'),
            ('LOT_MANAGER', 'Parking Lot Manager'),
            ('ADMIN', 'Administrator')
        ],
        default='CUSTOMER'
    )
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    preferred_payment_method = models.CharField(max_length=255, blank=True)
    reward_points = models.IntegerField(default=0)
    notification_settings = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.user} - {self.status}"
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} - {'Read' if self.read else 'Unread'}"