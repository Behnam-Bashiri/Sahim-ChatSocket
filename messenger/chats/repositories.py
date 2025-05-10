from .models import Chat, Message
from accounts.models import UserProfile
from django.db.models import Q


class ChatRepository:
    @staticmethod
    def create_chat(participants):
        chat = Chat.objects.create()
        chat.participants.set(participants)
        chat.save()
        return chat

    @staticmethod
    def get_chats_for_user(user):
        return Chat.objects.filter(participants=user)

    @staticmethod
    def get_chat_by_id(chat_id):
        return Chat.objects.filter(id=chat_id).first()


class MessageRepository:
    @staticmethod
    def create_message(chat, sender, content, media=None):
        message = Message(chat=chat, sender=sender, content=content, media=media)
        message.save()
        return message

    @staticmethod
    def get_messages_for_chat(chat):
        return Message.objects.filter(chat=chat)
