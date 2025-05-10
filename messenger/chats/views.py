# chat/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .services import ChatService
from accounts.models import UserProfile
from .serializers import MessageSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.db.models import Q
from .models import Chat


class ChatListView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        chats = ChatService.get_chats_for_user(user)
        data = []
        for chat in chats:
            messages = ChatService.get_messages_for_chat(chat)
            participants = [
                {
                    "phone_number": user.phone_number,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "profile_picture": (
                        user.profile_picture.url if user.profile_picture else None
                    ),
                }
                for user in chat.participants.all()
            ]
            data.append(
                {
                    "chat_id": chat.id,
                    "participants": participants,
                    "messages": MessageSerializer(messages, many=True).data,
                }
            )
        return Response(data, status=status.HTTP_200_OK)


class ChatUserListView(APIView):
    def get(self, request):
        search_query = request.query_params.get("search", "")
        users = UserProfile.objects.filter(
            Q(phone_number__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
        )
        data = [
            {
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile_picture": (
                    user.profile_picture.url if user.profile_picture else None
                ),
            }
            for user in users
        ]
        return Response(data, status=status.HTTP_200_OK)


class CreateChatView(APIView):
    def post(self, request):
        user1 = request.user
        user2_phone_number = request.data.get("user2_phone_number")
        user2 = get_object_or_404(UserProfile, phone_number=user2_phone_number)

        chat = ChatService.get_or_create_chat_with_user(user1, user2)

        return Response(
            {
                "chat_id": chat.id,
                "participants": [user.phone_number for user in chat.participants.all()],
            },
            status=status.HTTP_201_CREATED,
        )


class PreviousChatUsersView(APIView):
    def get(self, request):
        user = request.user
        chats = ChatService.get_chats_for_user(user)
        users = []

        for chat in chats:
            participants = chat.participants.all()
            for participant in participants:
                if participant != user:
                    users.append(
                        {
                            "phone_number": participant.phone_number,
                            "first_name": participant.first_name,
                            "last_name": participant.last_name,
                            "profile_picture": (
                                participant.profile_picture.url
                                if participant.profile_picture
                                else None
                            ),
                        }
                    )

        return Response(users, status=status.HTTP_200_OK)


class ChatMessagesWithUserView(APIView):
    def get(self, request, phone_number):
        user1 = request.user
        user2 = get_object_or_404(UserProfile, phone_number=phone_number)

        chat = (
            Chat.objects.filter(participants=user1).filter(participants=user2).first()
        )

        if not chat:
            return Response(
                {"detail": "No chat found between users."},
                status=status.HTTP_404_NOT_FOUND,
            )

        messages = chat.messages.all().order_by("timestamp")
        serialized_messages = MessageSerializer(messages, many=True)
        return Response(
            {
                "chat_id": chat.id,
                "participants": [p.phone_number for p in chat.participants.all()],
                "messages": serialized_messages.data,
            },
            status=status.HTTP_200_OK,
        )
