from rest_framework import generics, status
from rest_framework.response import Response
from .services import ChatService
from accounts.models import UserProfile
from .serializers import MessageSerializer, FileMessageSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.db.models import Q
from .models import Chat, FileMessage
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .tasks import compress_chat_file
from rest_framework import serializers
from .repositories import FileRepository
from rest_framework.pagination import PageNumberPagination
from accounts.services import UserProfileService


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ChatListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="دریافت لیست چت‌های کاربر",
        operation_description="این API همه چت‌هایی که کاربر در آن‌ها عضو است را همراه با پیام‌ها و اطلاعات شرکت‌کنندگان برمی‌گرداند.",
        responses={
            200: openapi.Response(
                "موفق",
                examples={
                    "application/json": {
                        "chat_id": 1,
                        "participants": [
                            {
                                "phone_number": "0912...",
                                "first_name": "Ali",
                                "last_name": "Ahmadi",
                            }
                        ],
                        "messages": [],
                    }
                },
            )
        },
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
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        operation_summary="جستجوی کاربران با فیلتر نام یا شماره",
        operation_description="امکان فیلتر کاربران بر اساس نام، نام خانوادگی یا شماره تلفن فراهم است.",
        manual_parameters=[
            openapi.Parameter(
                "phone_number",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="شماره تلفن",
            ),
            openapi.Parameter(
                "first_name",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="نام",
            ),
            openapi.Parameter(
                "last_name",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="نام خانوادگی",
            ),
        ],
        responses={
            200: openapi.Response(
                "لیست کاربران",
                examples={
                    "application/json": [
                        {
                            "phone_number": "0912...",
                            "first_name": "Ali",
                            "last_name": "Ahmadi",
                        }
                    ]
                },
            )
        },
    )
    def get(self, request):
        phone_number = request.query_params.get("phone_number", "").strip()
        first_name = request.query_params.get("first_name", "").strip()
        last_name = request.query_params.get("last_name", "").strip()

        users = UserProfileService.search_users_by_filters(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            exclude_user_id=request.user.id,
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
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="ایجاد چت جدید",
        operation_description="ایجاد یک چت بین کاربر جاری و کاربر دیگر از طریق شماره تلفن.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["user2_phone_number"],
            properties={
                "user2_phone_number": openapi.Schema(
                    type=openapi.TYPE_STRING, description="شماره تلفن طرف مقابل"
                )
            },
            example={"user2_phone_number": "09121234567"},
        ),
        responses={
            201: openapi.Response(
                "چت ایجاد شد",
                examples={
                    "application/json": {
                        "chat_id": 2,
                        "participants": ["0912...", "0935..."],
                    }
                },
            )
        },
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
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        operation_summary="کاربران قبلی چت",
        operation_description="برمی‌گرداند لیست کاربران یکتایی که کاربر با آن‌ها چت داشته است.",
        responses={
            200: openapi.Response(
                "لیست کاربران قبلی",
                examples={
                    "application/json": [
                        {
                            "phone_number": "0912...",
                            "first_name": "Sara",
                            "last_name": "Khosravi",
                        }
                    ]
                },
            )
        },
    )
    def get(self, request):
        contacts = ChatService.get_contacts_for_user(request.user)

        data = [
            {
                "phone_number": u.phone_number,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "profile_picture": u.profile_picture.url if u.profile_picture else None,
            }
            for u in contacts
        ]

        return Response(data, status=status.HTTP_200_OK)


class ChatMessagesWithUserView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        operation_summary="دریافت پیام‌های چت با یک کاربر خاص",
        operation_description="دریافت پیام‌های رد و بدل شده با یک کاربر خاص از طریق شماره تلفن.",
        responses={
            200: openapi.Response(
                "پیام‌ها",
                examples={
                    "application/json": {
                        "chat_id": 1,
                        "participants": ["0912...", "0935..."],
                        "messages": [],
                    }
                },
            ),
            404: "چت یافت نشد",
        },
    )
    def get(self, request, phone_number):
        try:
            result = ChatService.get_chat_messages_with_user(request.user, phone_number)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        serialized_messages = MessageSerializer(result["messages"], many=True)

        return Response(
            {
                "chat_id": result["chat"].id,
                "participants": [p.phone_number for p in result["participants"]],
                "messages": serialized_messages.data,
            },
            status=status.HTTP_200_OK,
        )


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class FileUploadAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="آپلود فایل",
        request_body=FileUploadSerializer,
        responses={
            200: openapi.Response(
                description="فایل با موفقیت آپلود شد",
                examples={"application/json": {"detail": "File uploaded successfully"}},
            ),
            400: openapi.Response(description="خطا در آپلود فایل"),
        },
    )
    def post(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)

        if request.user not in chat.participants.all():
            return Response({"error": "Unauthorized"}, status=403)

        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file provided"}, status=400)

        file_message = FileRepository.get_file_message(chat, request.user, file)

        compress_chat_file.delay(file_message.id)

        return Response(FileMessageSerializer(file_message).data, status=201)
