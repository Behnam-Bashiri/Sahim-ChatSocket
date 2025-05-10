# chat/services.py
from .repositories import ChatRepository, MessageRepository
from accounts.models import UserProfile


class ChatService:
    @staticmethod
    def create_chat_between_users(user1, user2):
        participants = [user1, user2]
        return ChatRepository.create_chat(participants)

    @staticmethod
    def get_chats_for_user(user):
        return ChatRepository.get_chats_for_user(user)

    @staticmethod
    def get_messages_for_chat(chat):
        return MessageRepository.get_messages_for_chat(chat)

    @staticmethod
    def get_or_create_chat_with_user(user, other_user):
        chat = ChatRepository.get_chats_with_user(user, other_user)
        if not chat:
            chat = ChatService.create_chat_between_users(user, other_user)
        return chat
