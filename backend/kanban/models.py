from django.db import models
from common.choices.priority import Priority


class Board(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, related_name="boards"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)


class Column(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="columns")
    position = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class Card(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name="cards")
    position = models.PositiveIntegerField()
    due_date = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(
        max_length=50, choices=Priority.choices, default="medium"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
