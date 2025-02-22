from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import models
from django.contrib.auth.models import User
import json

class NotificationType(models.TextChoices):
    BOOKING_CONFIRMATION = 'BOOKING_CONFIRMATION', 'Booking Confirmation'
    PARKING_REMINDER = 'PARKING_REMINDER', 'Parking Reminder'
    PAYMENT_SUCCESS = 'PAYMENT_SUCCESS', 'Payment Success'
    PAYMENT_FAILED = 'PAYMENT_FAILED', 'Payment Failed'
    SPACE_ALERT = 'SPACE_ALERT', 'Space Alert'
    SYSTEM_UPDATE = 'SYSTEM_UPDATE', 'System Update'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type} - {self.user.username}"

class NotificationService:
    @staticmethod
    def send_notification(user_id, notification_type, title, message, data=None):
        """Send notification to specific user"""
        user = User.objects.get(id=user_id)
        notification = Notification.objects.create(
            user=user,
            type=notification_type,
            title=title,
            message=message,
            data=data
        )

        # Send WebSocket notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "send_notification",
                "message": {
                    "id": notification.id,
                    "type": notification_type,
                    "title": title,
                    "message": message,
                    "data": data,
                    "created_at": notification.created_at.isoformat()
                }
            }
        )

    @staticmethod
    def send_bulk_notification(user_ids, notification_type, title, message, data=None):
        """Send notification to multiple users"""
        notifications = []
        for user_id in user_ids:
            NotificationService.send_notification(
                user_id, notification_type, title, message, data
            )

    @staticmethod
    def mark_as_read(notification_id, user_id):
        """Mark notification as read"""
        Notification.objects.filter(
            id=notification_id,
            user_id=user_id
        ).update(is_read=True)

    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications as read for a user"""
        Notification.objects.filter(
            user_id=user_id,
            is_read=False
        ).update(is_read=True) 