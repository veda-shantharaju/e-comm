from rest_framework import serializers
from .models import CustomUser,Address,PasswordResetOTP
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError


class UserPasswordChangeSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirmed_password = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ("id", "old_password", "new_password", "confirmed_password")

    def validate(self, data):

        if not self.context["request"].user.check_password(data.get("old_password")):
            raise serializers.ValidationError({"message": "Wrong password."})

        if data.get("confirmed_password") != data.get("new_password"):
            raise serializers.ValidationError(
                {"message": "Password must be confirmed correctly."}
            )

        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"])
        instance.save()
        return instance

class AddressSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Address
        fields = [
            'receiver_name', 'phone_number', 'alternate_phone_number',
            'address_line_1', 'address_line_2', 'city', 'state', 'postal_code',
            'country', 'address_type', 'is_default', 'latitude', 'longitude'
        ]

    def create(self, validated_data):
        user = self.context['request'].user  # Get the user from the request context

        # Check if the user is setting another address as default
        is_default = validated_data.get('is_default', False)
        
        if is_default:
            # If the new address is set to default, check if the user already has a default address
            existing_default_address = Address.objects.filter(user=user, is_default=True).first()
            if existing_default_address:
                # If the user already has a default address, raise an error
                raise ValidationError("You can only have one default address.")

        # Attach the user to the validated data
        validated_data['user'] = user
        
        # Create and return the address instance
        return Address.objects.create(**validated_data)


class CustomUserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    country_code = serializers.CharField(max_length=5, write_only=True)
    phone_number = serializers.CharField(max_length=15)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'country_code', 'password', 'confirm_password']
    
    def validate(self, data):
        """
        Ensure that the password and confirm_password match.
        Check if email or phone number already exists.
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Password and confirm password do not match."})
        
        existing_user_by_email = CustomUser.objects.filter(email=data['email']).exists()
        full_phone_number = f"{data['country_code']}{data['phone_number']}"
        existing_user_by_phone = CustomUser.objects.filter(phone_number=full_phone_number).exists()

        if existing_user_by_email or existing_user_by_phone:
            raise serializers.ValidationError({"detail": "User already exists. Try to login."})

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        full_phone_number = f"{validated_data['country_code']}{validated_data['phone_number']}"
        username = f"{validated_data['first_name']}_{validated_data['last_name']}"

        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=full_phone_number,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=username,
        )
        return user

    def to_representation(self, instance):
        """
        Override to exclude the password field from the response.
        """
        data = super().to_representation(instance)
        # Exclude the password field from the serialized response
        data.pop('password', None)
        return data
    
class PasswordResetRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField()

    def validate_identifier(self, value):
        """
        Validate if the identifier is either an email or a phone number.
        """
        if "@" not in value and not value.isdigit():
            raise serializers.ValidationError("Provide a valid email or phone number.")
        return value
    
class PasswordResetOTPVerifySerializer(serializers.Serializer):
    identifier = serializers.CharField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        """
        Validate OTP and ensure it matches with the user's record.
        """
        identifier = data.get('identifier')
        otp = data.get('otp')

        # Check if identifier is email or phone number
        try:
            user = None
            if "@" in identifier:  # Email
                user = CustomUser.objects.get(email=identifier)
            else:  # Phone number
                user = CustomUser.objects.get(phone_number=identifier)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with the given identifier does not exist.")

        # Validate OTP
        try:
            otp_record = PasswordResetOTP.objects.get(user=user, otp=otp)
            if otp_record.is_expired():
                raise serializers.ValidationError("OTP has expired.")
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP.")

        data['user'] = user
        return data
