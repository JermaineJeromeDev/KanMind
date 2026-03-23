"""
Serializers for the auth_app.
Handles user registration, validation, and public user profiles.
"""

# 2. Third-party (Django & DRF)
from rest_framework import serializers

# 3. Local
from ..models import CustomUser


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for handling new user registration.
    Includes password validation and creation logic.
    """
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        """
        Meta configuration for the RegistrationSerializer.
        """
        model = CustomUser
        fields = ["id", "fullname", "email", "password", "repeated_password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        """
        Validates that both password fields match.
        """
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                "Ungültige Anfragedaten. Die Passwörter stimmen nicht überein."
            )
        return attrs

    def create(self, validated_data):
        """
        Creates a new CustomUser instance using the email as username.
        """
        validated_data.pop("repeated_password")
        validated_data["username"] = validated_data["email"]
        return CustomUser.objects.create_user(**validated_data)


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Serializer for public user information.
    Used for board members and task assignments.
    """
    class Meta:
        """
        Meta configuration for the UserPublicSerializer.
        """
        model = CustomUser
        fields = ["id", "email", "fullname"]