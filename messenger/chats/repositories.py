# chat/repositories.py
from .models import Chat, Message
from accounts.models import UserProfile


class ChatRepository:
    @staticmethod
    def create_chat(participants):
        chat = Chat.objects.create()
        chat.participants.set(participants)

        if len(participants) == 2:
            user1, user2 = participants

            from_user = user1
            to_user = user2 if user1 != from_user else user1

            other_user = user2 if user1 == from_user else user1
            chat.chat_name = f"{other_user.first_name} {other_user.last_name}".strip()

        chat.save()
        return chat

    @staticmethod
    def get_chats_for_user(user):
        return Chat.objects.filter(participants=user)

    @staticmethod
    def get_chat_by_id(chat_id):
        return Chat.objects.filter(id=chat_id).first()

    @staticmethod
    def get_chats_with_user(user, other_user):
        return Chat.objects.filter(participants=user).filter(participants=other_user)


class MessageRepository:
    @staticmethod
    def create_message(chat, sender, content, message_type="text"):
        message = Message(
            chat=chat,
            sender=sender,
            content=content,
            message_type=message_type,
            is_read=False,
        )
        message.save()
        return message

    @staticmethod
    def get_messages_for_chat(chat):
        return Message.objects.filter(chat=chat)
