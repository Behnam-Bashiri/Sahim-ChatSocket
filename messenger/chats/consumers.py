import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from django.db import close_old_connections
from asgiref.sync import sync_to_async
from .models import Message, Chat
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.user = self.scope["user"]

        if not await self.user_in_chat(self.user, self.chat_id):
            await self.close()
            return

        self.group_name = f"chat_{self.chat_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        message_type = text_data_json["message_type"]
        file_url = text_data_json.get("file_url")

        chat = await database_sync_to_async(Chat.objects.get)(id=self.chat_id)
        sender = self.user

        if message_type == "file" and file_url:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat_message",
                    "message_type": message_type,
                    "file_url": file_url,
                    "sender": sender.phone_number,
                },
            )
        else:
            await database_sync_to_async(Message.objects.create)(
                chat=chat, sender=sender, content=message, message_type=message_type
            )
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "message_type": message_type,
                    "sender": sender.phone_number,
                },
            )

    async def chat_message(self, event):
        message = event["message"]
        message_type = event["message_type"]
        sender = event["sender"]

        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "message_type": message_type,
                    "sender": sender,
                }
            )
        )

    @sync_to_async
    def user_in_chat(self, user, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id)
            return chat.participants.filter(id=user.id).exists()
        except Chat.DoesNotExist:
            return False
