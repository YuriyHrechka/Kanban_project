from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from common.enums.errors import ErrorEnum
from django.db import IntegrityError


class UserAuthSerializer(serializers.ModelSerializer):
    """
    The UserAuthSerializer class in Python handles user authentication data serialization and password
    hashing during user creation.
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
        The `create` function creates a new user with the provided validated data and password in a Django
        custom user model.

        Args:
          validated_data:

        Returns:
          The `user` object is being returned.
        """
        password = validated_data.pop("password", None)

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
        The function `validate` checks the password attribute and then calls the superclass's validate
        method.
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
        qs = CustomUser.objects.filter(username=value)

        if getattr(self, "instance", None):
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(ErrorEnum.USERNAME_IS_TAKEN.value)
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username"]
        read_only_fields = ["id", "username"]
