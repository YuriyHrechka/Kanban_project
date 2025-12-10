from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    The class `CustomUser` extends `AbstractUser` and adds a unique `username` field with a maximum
    """

    username = models.CharField(max_length=150, unique=True)
