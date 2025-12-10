from rest_framework import serializers
from kanban.models import Card, Column, Board
from common.choices.priority import Priority
from common.enums.errors import ErrorEnum


class CardNestedSerializer(serializers.ModelSerializer):
    """Lightweight card serializer for nested use inside Column."""

    class Meta:
        model = Card
        fields = [
            "id",
            "title",
            "description",
            "position",
            "due_date",
            "priority",
        ]
        read_only_fields = fields


class ColumnNestedSerializer(serializers.ModelSerializer):
    """Column serializer with nested cards."""

    cards = CardNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Column
        fields = ["id", "title", "position", "cards"]
        read_only_fields = fields


class BoardDetailSerializer(serializers.ModelSerializer):
    """Board serializer with nested columns and cards."""

    columns = ColumnNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "description",
            "is_archived",
            "created_at",
            "updated_at",
            "columns",
        ]
        read_only_fields = fields


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for the Board model.
    Provides validation and serialization for board-related fields.
    """

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "description",
            "owner",
            "created_at",
            "updated_at",
            "is_archived",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "owner"]


class ColumnDetailSerializer(serializers.ModelSerializer):
    """Column serializer with nested cards."""

    cards = CardNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Column
        fields = ["id", "title", "board", "position", "created_at", "cards"]
        read_only_fields = ["id", "created_at", "board"]


class ColumnSerializer(serializers.ModelSerializer):
    """
    Serializer for the Column model.
    Provides validation and serialization for column-related fields.
    """

    class Meta:
        model = Column
        fields = ["id", "title", "board", "position", "created_at"]
        read_only_fields = ["id", "created_at"]


class CardSerializer(serializers.ModelSerializer):
    """
    Serializer for the Card model.
    Provides validation and serialization for card-related fields,
    including custom validation for priority.
    """

    class Meta:
        model = Card
        fields = [
            "id",
            "title",
            "description",
            "column",
            "position",
            "due_date",
            "priority",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_priority(self, value):
        """
        Validate the priority field to ensure it matches allowed values.

        :param value: The provided priority value.
        :return: The validated priority value if valid.
        :raises serializers.ValidationError: If the value is not a valid priority.
        """
        if value not in Priority.values:
            raise serializers.ValidationError(ErrorEnum.INVALID_PRIORITY.value)
        return value
