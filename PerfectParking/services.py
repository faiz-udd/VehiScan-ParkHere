from .models import Booking, Payment, ParkingSpot
from django.utils import timezone
from decimal import Decimal
import stripe
from stripe import error as StripeError
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class BookingService:
    @staticmethod
    def create_booking(user, parking_spot, start_time, end_time):
        total_cost = BookingService.calculate_total_cost(parking_spot, start_time, end_time)
        booking = Booking.objects.create(
            user=user,
            parking_spot=parking_spot,
            start_time=start_time,
            end_time=end_time,
            total_cost=total_cost,
            status='PENDING'
        )
        return booking

    @staticmethod
    def calculate_total_cost(parking_spot, start_time, end_time):
        duration = (end_time - start_time).total_seconds() / 3600  # duration in hours
        parking_lot = parking_spot.parking_lot
        total_cost = duration * parking_lot.get_current_price()
        return round(total_cost, 2)

    @staticmethod
    def confirm_booking(booking):
        booking.status = 'CONFIRMED'
        booking.save()
        parking_spot = booking.parking_spot
        parking_spot.is_occupied = True
        parking_spot.save()

    @staticmethod
    def cancel_booking(booking):
        booking.status = 'CANCELLED'
        booking.save()
        parking_spot = booking.parking_spot
        parking_spot.is_occupied = False
        parking_spot.save()

class PaymentService:
    @staticmethod
    def create_payment(booking, amount):
        payment = Payment.objects.create(
            user=booking.user,
            booking=booking,
            amount=amount,
            status='PENDING'
        )
        return payment

    @staticmethod
    def process_payment(payment, token):
        try:
            charge = stripe.Charge.create(
                amount=int(payment.amount * 100),  # amount in cents
                currency='usd',
                source=token,
                description=f"Payment for booking {payment.booking.id}"
            )
            payment.status = 'COMPLETED'
            payment.save()
            return charge
        except StripeError as e:
            payment.status = 'FAILED'
            payment.save()
            raise e