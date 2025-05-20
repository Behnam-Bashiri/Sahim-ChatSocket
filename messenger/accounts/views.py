# accounts/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .services import AuthService
from .serializers import UserProfileSerializer, PhoneOTPSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .repositories import UserProfileRepository, PhoneOTPRepository
from .models import UserProfile
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = PhoneOTPSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="تأیید کد OTP",
        request_body=PhoneOTPSerializer,
        responses={
            200: openapi.Response(
                description="کد OTP با موفقیت تأیید شد",
                examples={
                    "application/json": {
                        "detail": "OTP verified successfully",
                        "access_token": "your_access_token_here",
                        "refresh_token": "your_refresh_token_here",
                    }
                },
            ),
            400: openapi.Response(description="کد OTP معتبر نیست"),
        },
    )
    def post(self, request):
        phone_number = request.data.get("phone_number")
        otp_code = request.data.get("otp_code")

        try:
            is_valid = AuthService.verify_otp(phone_number, otp_code)

            if not is_valid:
                raise ValidationError("Invalid OTP code")
            user = UserProfileRepository.get_user_by_phone(phone_number)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            PhoneOTPRepository.delete_otp(phone_number, otp_code)

            return Response(
                {
                    "detail": "OTP verified successfully",
                    "access_token": access_token,
                    "refresh_token": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RegisterOrCreateOTPView(generics.GenericAPIView):
    serializer_class = PhoneOTPSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="ثبت نام یا ارسال کد OTP برای کاربر",
        request_body=PhoneOTPSerializer,
        responses={
            201: openapi.Response(
                description="کاربر با موفقیت ثبت شد یا کاربر از قبل وجود دارد",
                examples={
                    "application/json": {
                        "detail": "User registered successfully",
                        "otp_code": "123456",
                    }
                },
            ),
            400: openapi.Response(description="خطا در ثبت نام یا ارسال کد OTP"),
        },
    )
    def post(self, request):
        phone_number = request.data.get("phone_number")
        otp_code = request.data.get("otp_code")
        user = UserProfileRepository.get_user_by_phone(phone_number)

        if user:
            otp = AuthService.create_otp(phone_number)
            return Response({"otp_code": otp.otp_code}, status=status.HTTP_200_OK)
        try:
            user, created = AuthService.register_or_get_user(phone_number, otp_code)
            otp = AuthService.create_otp(phone_number)

            return Response(
                {
                    "detail": (
                        "User registered successfully"
                        if created
                        else "User already exists"
                    ),
                    "otp_code": otp.otp_code,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="دریافت پروفایل کاربری",
        responses={
            200: openapi.Response(description="اطلاعات پروفایل کاربر"),
            400: openapi.Response(description="خطا در به‌روزرسانی پروفایل"),
        },
    )
    def get_object(self):
        user_id = self.request.user.id
        return get_object_or_404(UserProfile, id=user_id)

    @swagger_auto_schema(
        operation_summary="به‌روزرسانی پروفایل کاربری",
        request_body=UserProfileSerializer,
        responses={
            200: openapi.Response(description="پروفایل با موفقیت به‌روزرسانی شد"),
            400: openapi.Response(description="خطا در به‌روزرسانی پروفایل"),
        },
    )
    def put(self, request, *args, **kwargs):
        user_profile = self.get_object()
        serializer = self.get_serializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="دریافت پروفایل کاربری",
        responses={200: openapi.Response(description="اطلاعات پروفایل کاربر")},
    )
    def get(self, request, *args, **kwargs):
        user_profile = self.get_object()
        serializer = self.get_serializer(user_profile)
        return Response(serializer.data)


class UserListView(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["phone_number"]
    ordering_fields = [
        "phone_number",
    ]
    ordering = ["phone_number"]

    pagination_class = PageNumberPagination

    @swagger_auto_schema(
        operation_summary="لیست کاربران با قابلیت جست‌وجو، مرتب‌سازی و صفحه‌بندی",
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="جست‌وجو بر اساس شماره یا نام کاربری",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="مرتب‌سازی مثل ordering=phone_number",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="شماره صفحه",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="تعداد آیتم در هر صفحه",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    def get_queryset(self):
        search = self.request.query_params.get("search")
        return UserProfileRepository.list_users(search)
