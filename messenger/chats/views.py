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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import FileMessage
from .serializers import FileMessageSerializer
from .tasks import compress_chat_file


class ChatListView(generics.ListAPIView):
    serializer_class = MessageSerializer

    @swagger_auto_schema(
        operation_summary="دریافت لیست چت‌های کاربر",
        responses={200: "لیست چت‌ها با پیام‌ها و اطلاعات کاربران"},
    )
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
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="دریافت لیست کاربران با قابلیت جست‌وجو",
        manual_parameters=[
            openapi.Parameter(
                "phone_number",
                openapi.IN_QUERY,
                description="جست‌وجو با شماره تلفن",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "first_name",
                openapi.IN_QUERY,
                description="جست‌وجو با نام",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "last_name",
                openapi.IN_QUERY,
                description="جست‌وجو با نام خانوادگی",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: "لیست کاربران پیدا شده"},
    )
    def get(self, request):
        phone_number = request.query_params.get("phone_number", "").strip()
        first_name = request.query_params.get("first_name", "").strip()
        last_name = request.query_params.get("last_name", "").strip()

        filters = Q()

        if phone_number:
            filters &= Q(phone_number__icontains=phone_number)
        if first_name:
            filters &= Q(first_name__icontains=first_name)
        if last_name:
            filters &= Q(last_name__icontains=last_name)

        users = UserProfile.objects.filter(filters).exclude(id=request.user.id)

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
    @swagger_auto_schema(
        operation_summary="ایجاد چت جدید بین دو کاربر",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["user2_phone_number"],
            properties={
                "user2_phone_number": openapi.Schema(
                    type=openapi.TYPE_STRING, description="شماره تلفن کاربر دوم"
                ),
            },
            example={"user2_phone_number": "09121234567"},
        ),
        responses={201: "چت با موفقیت ساخته شد"},
    )
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
    @swagger_auto_schema(
        operation_summary="دریافت لیست کاربران چت‌شده قبلی",
        responses={200: "لیست یکتا از کاربرانی که قبلاً با آن‌ها چت شده"},
    )
    def get(self, request):
        user = request.user
        chats = ChatService.get_chats_for_user(user)
        user_ids = set()

        for chat in chats:
            participants = chat.participants.exclude(id=user.id)
            user_ids.update(participants.values_list("id", flat=True))

        # گرفتن اطلاعات کاربران یکتا
        users = UserProfile.objects.filter(id__in=user_ids)

        data = [
            {
                "phone_number": u.phone_number,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "profile_picture": u.profile_picture.url if u.profile_picture else None,
            }
            for u in users
        ]

        return Response(data, status=status.HTTP_200_OK)


class ChatMessagesWithUserView(APIView):
    @swagger_auto_schema(
        operation_summary="دریافت پیام‌های یک چت بین دو کاربر",
        responses={200: "پیام‌های چت", 404: "چت بین کاربران یافت نشد"},
    )
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


class FileUploadAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)

        if request.user not in chat.participants.all():
            return Response({"error": "Unauthorized"}, status=403)

        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file provided"}, status=400)

        file_message = FileMessage.objects.create(
            chat=chat, sender=request.user, file=file
        )

        compress_chat_file.delay(file_message.id)

        return Response(FileMessageSerializer(file_message).data, status=201)
