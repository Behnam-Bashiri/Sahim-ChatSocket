from typing import List, Optional, Tuple, Union, IO
from .models import Chat, Message, FileMessage
from accounts.models import UserProfile
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet


class ChatRepository:
    @staticmethod
    def create_chat(participants: List[UserProfile]) -> Chat:
        chat = Chat.objects.create()
        chat.participants.set(participants)

        if len(participants) == 2:
            user1, user2 = participants
            other_user = user2 if user1 == participants[0] else user1
            chat.chat_name = f"{other_user.first_name} {other_user.last_name}".strip()

        chat.save()
        return chat

    @staticmethod
    def get_chats_for_user(user: UserProfile) -> QuerySet[Chat]:
        return Chat.objects.filter(participants=user)

    @staticmethod
    def get_chat_by_id(chat_id: int) -> Optional[Chat]:
        return Chat.objects.filter(id=chat_id).first()

    @staticmethod
    def get_chats_with_user(
        user: UserProfile, other_user: UserProfile
    ) -> QuerySet[Chat]:
        return Chat.objects.filter(participants=user).filter(participants=other_user)

    @staticmethod
    def get_chat_between_users(
        user1: UserProfile, phone_number: str
    ) -> Tuple[Optional[Chat], UserProfile]:
        user2 = get_object_or_404(UserProfile, phone_number=phone_number)
        chat = (
            Chat.objects.filter(participants=user1).filter(participants=user2).first()
        )
        return chat, user2


class MessageRepository:
    @staticmethod
    def create_message(
        chat: Chat, sender: UserProfile, content: str, message_type: str = "text"
    ) -> Message:
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
    def get_messages_for_chat(chat: Chat) -> QuerySet[Message]:
        return Message.objects.filter(chat=chat)

    @staticmethod
    def get_ordered_messages_for_chat(chat: Chat) -> QuerySet[Message]:
        return Message.objects.filter(chat=chat).order_by("timestamp")


class FileRepository:
    @staticmethod
    def get_file_message(chat: Chat, sender: UserProfile, fileIO: IO) -> FileMessage:
        file_message = FileMessage.objects.create(chat=chat, sender=sender, file=fileIO)
        return file_message
