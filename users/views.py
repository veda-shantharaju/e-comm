from django.shortcuts import render
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import login
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core import validators
from .models import CustomUser
from .serializers import UserPasswordChangeSerializer
from rest_framework.generics import CreateAPIView
from django.core import exceptions
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from knox.views import LogoutView as KnoxLogoutView

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