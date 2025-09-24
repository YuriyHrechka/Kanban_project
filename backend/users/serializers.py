from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from common.enums.errors import ErrorEnum


class UserAuthSerializer(serializers.ModelSerializer):
    """
    The UserAuthSerializer class in Python handles user authentication data serialization and password
    hashing during user creation.
    """

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = CustomUser
        fields = ["username", "password"]

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

        user = CustomUser.objects.create_user(**validated_data, password=password)
        user.is_active = True
        return user

    def validate(self, attrs):
        """
        The function `validate` checks the password attribute and then calls the superclass's validate
        method.
        """
        validate_password(attrs.get("password"))
        return super().validate(attrs)

    def validate_username(self, value):
        qs = CustomUser.objects.filter(username=value)
        if qs.exists():
            raise serializers.ValidationError(ErrorEnum.USERNAME_IS_TAKEN.value)
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username"]
        read_only_fields = ["id", "username"]
