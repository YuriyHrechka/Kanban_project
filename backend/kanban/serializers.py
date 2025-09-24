from rest_framework import serializers
from kanban.models import Card, Column, Board
from common.choices.priority import Priority
from common.enums.errors import ErrorEnum


class BoardSerializer(serializers.ModelSerializer):
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


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = ["id", "title", "board", "position", "created_at"]
        read_only_fields = ["id", "created_at"]


class CardSerializer(serializers.ModelSerializer):
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
        if value not in Priority.values:
            raise serializers.ValidationError(ErrorEnum.INVALID_PRIORITY.value)
        return value
