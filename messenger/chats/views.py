from rest_framework import generics, status
from rest_framework.response import Response
from .services import ChatService, MessageService
from .serializers import ChatSerializer, MessageSerializer


class CreateChatView(generics.CreateAPIView):
    serializer_class = ChatSerializer

    def perform_create(self, serializer):
        user = self.request.user
        participant_id = self.request.data.get("participant_id")
        chat = ChatService.create_chat(user, participant_id)
        serializer.save()

    def create(self, request, *args, **kwargs):
        user = self.request.user
        participant_id = request.data.get("participant_id")
        chat = ChatService.create_chat(user, participant_id)
        return Response({"chat_id": chat.id}, status=status.HTTP_201_CREATED)


class ChatListView(generics.ListAPIView):
    serializer_class = ChatSerializer

    def get_queryset(self):
        return ChatService.get_user_chats(self.request.user)


class MessageListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat_id = self.kwargs["chat_id"]
        return MessageService.get_messages_for_chat(chat_id)

    def perform_create(self, serializer):
        chat_id = self.request.data["chat"]
        sender = self.request.user
        content = self.request.data["content"]
        media = self.request.data.get("media")
        message = MessageService.send_message(chat_id, sender, content, media)
        serializer.save(sender=sender, chat=message.chat)
