from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import threading
import logging

logger = logging.getLogger(__name__)

class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        threading.Thread.__init__(self)

    def run(self):
        try:
            msg = EmailMultiAlternatives(
                self.subject,
                strip_tags(self.html_content),
                settings.DEFAULT_FROM_EMAIL,
                self.recipient_list
            )
            msg.attach_alternative(self.html_content, "text/html")
            msg.send()
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            # Could add retry logic here

class EmailService:
    @staticmethod
    def send_async_email(subject, template_name, context, recipient_list):
        """Send email asynchronously"""
        html_content = render_to_string(template_name, context)
        EmailThread(subject, html_content, recipient_list).start()

    @classmethod
    def send_booking_confirmation(cls, booking):
        """Send booking confirmation email"""
        context = {
            'user': booking.user,
            'booking': booking,
            'parking_lot': booking.parking_lot,
            'qr_code': booking.generate_qr_code()
        }
        
        cls.send_async_email(
            subject='Your Parking Booking Confirmation',
            template_name='emails/booking_confirmation.html',
            context=context,
            recipient_list=[booking.user.email]
        )

    @classmethod
    def send_reminder(cls, booking):
        """Send booking reminder email"""
        context = {
            'user': booking.user,
            'booking': booking,
            'parking_lot': booking.parking_lot
        }
        
        cls.send_async_email(
            subject='Your Parking Reminder',
            template_name='emails/booking_reminder.html',
            context=context,
            recipient_list=[booking.user.email]
        )

    @classmethod
    def send_payment_receipt(cls, payment):
        """Send payment receipt"""
        context = {
            'user': payment.booking.user,
            'payment': payment,
            'booking': payment.booking
        }
        
        cls.send_async_email(
            subject='Payment Receipt',
            template_name='emails/payment_receipt.html',
            context=context,
            recipient_list=[payment.booking.user.email]
        ) 