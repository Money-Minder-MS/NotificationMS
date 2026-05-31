import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # URL: ws://localhost:8086/ws/notifications/{user_id}/
        self.user_id   = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"user_{self.user_id}"

        # Rejoindre le groupe de l'utilisateur
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        await self.send(text_data=json.dumps({
            'message': f'Connecté aux notifications (user {self.user_id})'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Reçoit un message du groupe et l'envoie au client WebSocket
    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event['notification']))