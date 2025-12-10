from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from common.enums.errors import ErrorEnum
from django.db import IntegrityError


class UserAuthSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration and authentication.
    """

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)
    confirm_password = serializers.CharField(
        max_length=128, write_only=True, required=False
    )

    class Meta:
        model = CustomUser
        fields = ["username", "password", "confirm_password"]

    def create(self, validated_data):
        """
        Create a new user with the provided validated data.

        :param validated_data: The validated data from the serializer.
        :return: The created user instance.
        """
        password = validated_data.pop("password", None)
        validated_data.pop("confirm_password", None)

        try:
            user = CustomUser.objects.create_user(**validated_data, password=password)
        except IntegrityError:
            raise serializers.ValidationError(
                {"username": ErrorEnum.USERNAME_IS_TAKEN.value}
            )

        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])

        return user

    def validate(self, attrs):
        """
        Validate the provided attributes, including password confirmation and strength.

        :param attrs: The incoming attributes to validate.
        :return: The validated attributes.
        """
        password = attrs.get("password")
        if not password:
            raise serializers.ValidationError({"password": ErrorEnum.FIELD_REQUIRED})

        confirm = attrs.get("confirm_password")
        if confirm is not None and password != confirm:
            raise serializers.ValidationError(
                {"confirm_password": ErrorEnum.PASSWORDS_DONT_MATCH.value}
            )

        validate_password(password)
        return super().validate(attrs)

    def validate_username(self, value):
        """
        Validate that the username is not already taken.

        :param value: The username to validate.
        :return: The validated username.
        """
        qs = CustomUser.objects.filter(username=value)

        if getattr(self, "instance", None):
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(ErrorEnum.USERNAME_IS_TAKEN.value)
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for returning basic user profile data.
    """

    class Meta:
        model = CustomUser
        fields = ["id", "username"]
        read_only_fields = ["id", "username"]
