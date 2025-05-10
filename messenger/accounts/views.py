# accounts/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .services import AuthService
from .serializers import UserProfileSerializer, PhoneOTPSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .repositories import UserProfileRepository
from .models import UserProfile


class RegisterOrCreateOTPView(generics.GenericAPIView):
    serializer_class = PhoneOTPSerializer

    def post(self, request):
        phone_number = request.data.get("phone_number")
        otp_code = request.data.get("otp_code")
        user = UserProfileRepository.get_user_by_phone(phone_number)

        if user:
            otp = AuthService.create_otp(phone_number)
            return Response({"otp_code": otp.otp_code}, status=status.HTTP_200_OK)

        try:
            user, created = AuthService.register_or_get_user(phone_number, otp_code)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            otp = AuthService.create_otp(phone_number)

            return Response(
                {
                    "detail": (
                        "User registered successfully"
                        if created
                        else "User already exists"
                    ),
                    "access_token": access_token,
                    "otp_code": otp.otp_code,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()

    def get_object(self):
        return (
            self.request.user
        )  # فرض بر این است که در هر درخواست JWT token برای کاربر ارسال می‌شود

    def put(self, request, *args, **kwargs):
        user_profile = self.get_object()
        serializer = self.get_serializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        user_profile = self.get_object()
        serializer = self.get_serializer(user_profile)
        return Response(serializer.data)
