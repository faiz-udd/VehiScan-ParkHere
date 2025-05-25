import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ParkingLot, Booking, Notification
from django.contrib.auth.models import User

class ParkingLotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.parking_lot_id = self.scope['url_route']['kwargs']['parking_lot_id']
        self.room_group_name = f'parking_lot_{self.parking_lot_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'occupancy_update':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'occupancy_update',
                    'data': text_data_json.get('data')
                }
            )

    async def occupancy_update(self, event):
        await self.send(text_data=json.dumps(event['data']))

class BookingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.booking_id = self.scope['url_route']['kwargs']['booking_id']
        self.room_group_name = f'booking_{self.booking_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'status_update':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'status_update',
                    'data': text_data_json.get('data')
                }
            )

    async def status_update(self, event):
        await self.send(text_data=json.dumps(event['data']))

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        self.user_id = str(self.scope["user"].id)
        self.room_group_name = f'notifications_{self.user_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'mark_read':
            notification_id = text_data_json.get('notification_id')
            await self.mark_notification_read(notification_id)

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user_id=self.user_id
            )
            notification.read = True
            notification.save()
        except Notification.DoesNotExist:
            pass

    async def notification_message(self, event):
        await self.send(text_data=json.dumps(event['data'])) 