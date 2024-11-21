from django.shortcuts import render
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import login
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import AddressSerializer,CustomUserRegisterSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from knox.views import LogoutView as KnoxLogoutView
from knox.models import AuthToken
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from .utils import send_sms
from users.serializers import *
# Create your views here.
class UserLoginAPIView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        response = super(UserLoginAPIView, self).post(request, format=None)
        response.data["id"] = user.id
        response.data["name"] = f"{user.first_name} {user.last_name}"
        return response
    
class UserPasswordChangeApiView(APIView):
    permission_classes = [IsAuthenticated]
    # queryset = CustomUser.objects.all().order_by("-id")
    # serializer_class = UserPasswordChangeSerializer

    def validate_password(self, password):
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({"message": list(e.messages)})

    def post(self, request, *args, **kwargs):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        confirmed_password = request.data.get("confirmed_password")

        if not old_password or not new_password or not confirmed_password:
            return Response({"success": False, "message": "Please enter all password fields."}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.check_password(old_password):
            return Response({"success": False, "message": "Old password is not correct."}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirmed_password:
            return Response({"success": False, "message": "New password and confirm password do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            self.validate_password(new_password)
        except serializers.ValidationError as e:
            return Response({"success": False, "message": e.detail}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(new_password)
        request.user.save()

        return Response({"success": True, "message": "Password has been changed successfully."}, status=status.HTTP_200_OK)
    
class CustomLogoutView(KnoxLogoutView):
    def post(self, request, format=None):
        response = super().post(request, format=None)
        return Response({"success": True, "message": "Successfully logged out."}, status=status.HTTP_200_OK)
    
class AddressCreateView(APIView):
    def post(self, request):
        # Pass the request to the serializer context
        serializer = AddressSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            address = serializer.save()
            return Response(
                {"message": "Address created successfully", "address": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RegisterView(APIView):
    """
    Handle user registration.
    """
    def post(self, request, *args, **kwargs):
        serializer = CustomUserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate a Knox token for the user
            token = AuthToken.objects.create(user)[1]
            return Response(
                {
                    "message": "User registered successfully",
                    "token": token,
                    "user": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class LoginView(KnoxLoginView):
    """
    Common Login
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        identifier = request.data.get("identifier")
        password = request.data.get("password")
        
        user = None
        if identifier:
            user = CustomUser.objects.filter(
                Q(phone_number__icontains=identifier) | 
                Q(email__iexact=identifier)
            ).first()
        
        if user:
            auth_data = {"username": user.username, "password": password}
            serializer = AuthTokenSerializer(data=auth_data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]
            
            login(request, user)
            response = super(LoginView, self).post(request, format=None)
            response.data.update({
                "id": user.id,
                "name": f"{user.username}",
            })
            return response
        else:
            return Response(
                {"message": "User not found."},
                status=status.HTTP_400_BAD_REQUEST
            )

class RequestPasswordResetView(APIView):
    """
    Handle OTP requests for password reset.
    """

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data['identifier']

        # Get user by identifier
        try:
            user = None
            if "@" in identifier:  # Email
                user = CustomUser.objects.get(email=identifier)
            else:  # Phone number
                user = CustomUser.objects.get(phone_number=identifier)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP
        otp_record = PasswordResetOTP.generate_otp(user)

        # Send OTP
        if "@" in identifier:  # Send via email
            send_mail(
                "Password Reset OTP",
                f"Your OTP is {otp_record.otp}. It will expire in 10 minutes.",
                "no-reply@example.com",
                [user.email],
                fail_silently=False,
            )
        else:  # Send via SMS (assuming you have the `send_sms` function)
            send_sms(user.phone_number, f"Your OTP is {otp_record.otp}. It will expire in 10 minutes.")

        return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)
    
    
class VerifyOTPAndResetPasswordView(APIView):
    """
    Verify OTP and reset the user's password.
    """

    def post(self, request):
        serializer = PasswordResetOTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        new_password = serializer.validated_data['new_password']

        # Set the new password
        user.set_password(new_password)
        user.save()

        # Delete the used OTP
        PasswordResetOTP.objects.filter(user=user).delete()

        return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)
