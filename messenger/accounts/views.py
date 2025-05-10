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


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = PhoneOTPSerializer
    permission_classes = [AllowAny]

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
                },
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RegisterOrCreateOTPView(generics.GenericAPIView):
    serializer_class = PhoneOTPSerializer
    permission_classes = [AllowAny]

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

    def get_object(self):
        user_id = self.request.user.id
        return get_object_or_404(UserProfile, id=user_id)

    def put(self, request, *args, **kwargs):
        user_profile = self.get_object()
        serializer = self.get_serializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        print(request.user)
        user_profile = self.get_object()
        serializer = self.get_serializer(user_profile)
        return Response(serializer.data)


class UserListView(generics.ListAPIView):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        query = self.request.query_params.get("search", None)
        if query:
            return UserProfile.objects.filter(
                Q(phone_number__icontains=query) | Q(username__icontains=query)
            )
        return UserProfile.objects.all()
