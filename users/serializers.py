from rest_framework import serializers
from .models import CustomUser



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