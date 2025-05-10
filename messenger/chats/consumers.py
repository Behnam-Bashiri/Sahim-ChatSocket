import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import UserProfile
from chats.models import Chat, Message
import logging

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.chat_id}"

        # Add to group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Accept connection
        await self.accept()

    async def disconnect(self, close_code):
        # Remove from group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        logger.info("Receiving message...")

        # تلاش برای تجزیه داده‌ها
        try:
            data = json.loads(text_data)
            message = data["message"]
        except json.JSONDecodeError:
            logger.error("Failed to decode message: %s", text_data)
            return

        logger.info("Message received: %s", message)

        sender = self.scope["user"]

        # اطمینان از احراز هویت فرستنده
        if not sender.is_authenticated:
            logger.warning("Unauthenticated user tried to send a message.")
            await self.close()
            return

        # تلاش برای بازیابی چت
        chat = await self.get_chat(self.chat_id)
        if not chat:
            logger.error("Chat not found for chat_id: %s", self.chat_id)
            await self.close()
            return

        # ایجاد پیام
        msg = await self.create_message(chat, sender, message)
        logger.info("Message created with ID: %s, timestamp: %s", msg.id, msg.timestamp)

        # ارسال پیام به گروه
        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": sender.phone_number,
                    "timestamp": str(msg.timestamp),
                },
            )
            logger.info("Message sent to group: %s", self.room_group_name)
        except Exception as e:
            logger.error("Error sending message to group: %s", e)

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_user(self, phone_number):
        try:
            return UserProfile.objects.get(phone_number=phone_number)
        except UserProfile.DoesNotExist:
            return None

    @database_sync_to_async
    def get_chat(self, chat_id):
        try:
            return Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return None

    @database_sync_to_async
    def create_message(self, chat, sender, content):
        return Message.objects.create(chat=chat, sender=sender, content=content)
