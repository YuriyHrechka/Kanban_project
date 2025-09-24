from enum import Enum


class ErrorEnum(Enum):
    """Enumeration for error messages."""

    INVALID_PRIORITY = "Invalid priority level."
    USERNAME_IS_TAKEN = "Username is already taken."
    PASSWORDS_DONT_MATCH = "Passwords dont match"
    FIELD_REQUIRED = "This field is required."
