# chat/services.py
from .repositories import ChatRepository, MessageRepository
from accounts.models import UserProfile
from rest_framework.exceptions import NotFound
from accounts.repositories import UserProfileRepository


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

    @staticmethod
    def get_chat_messages_with_user(current_user, phone_number):
        try:
            other_user = UserProfile.objects.get(phone_number=phone_number)
        except UserProfile.DoesNotExist:
            raise NotFound("User with this phone number not found.")

        chat_qs = ChatRepository.get_chats_with_user(current_user, other_user)
        chat = chat_qs.first()

        if not chat:
            raise NotFound("No chat found between users.")

        messages = MessageRepository.get_ordered_messages_for_chat(chat)

        return {
            "chat": chat,
            "participants": chat.participants.all(),
            "messages": messages,
        }

    @staticmethod
    def get_contacts_for_user(user):
        chats = ChatRepository.get_chats_for_user(user).prefetch_related("participants")

        other_user_ids: set[int] = set()
        for chat in chats:
            other_user_ids.update(
                chat.participants.exclude(id=user.id).values_list("id", flat=True)
            )

        return UserProfileRepository.get_users_by_ids(other_user_ids)
