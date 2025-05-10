from .repositories import ChatRepository, MessageRepository
from .models import Chat, Message
from accounts.models import UserProfile


class ChatService:
    @staticmethod
    def create_chat(user, participant_id):
        participant = UserProfile.objects.get(id=participant_id)
        participants = [user, participant]
        chat = ChatRepository.create_chat(participants)
        return chat

    @staticmethod
    def get_user_chats(user):
        chats = ChatRepository.get_chats_for_user(user)
        return chats

    @staticmethod
    def get_messages_for_chat(chat_id):
        chat = ChatRepository.get_chat_by_id(chat_id)
        if not chat:
            raise ValueError("Chat not found")
        return MessageRepository.get_messages_for_chat(chat)


class MessageService:
    @staticmethod
    def send_message(chat_id, sender, content, media=None):
        chat = ChatRepository.get_chat_by_id(chat_id)
        if not chat:
            raise ValueError("Chat not found")
        message = MessageRepository.create_message(chat, sender, content, media)
        return message
