from django.db import models


class Priority(models.TextChoices):
    """
    The class Priority defines choices for priority levels with corresponding labels in a Django model.
    """

    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
