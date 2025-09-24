from enum import Enum


class ErrorEnum(Enum):
    """Enumeration for error messages."""

    INVALID_PRIORITY = "Invalid priority level."
    USERNAME_IS_TAKEN = "Username is already taken."
    PASSWORDS_DONT_MATCH = "Passwords dont match"
    FIELD_REQUIRED = "This field is required."
    CANNOT_CREATE_COLUMN_ON_ANOTHER_USERS_BOARD = (
        "Cannot create column on a board you do not own."
    )
    CANNOT_CREATE_CARD_ON_ANOTHER_USERS_COLUMN = (
        "Cannot create card inside a column you do not own."
    )
    CANNOT_MOVE_UPDATE_COLUMN_TO_ANOTHER_USERS_BOARD = (
        "Cannot move/update column to a board you do not own."
    )
    CANNOT_MOVE_UPDATE_CARD_TO_ANOTHER_USERS_COLUMN = (
        "Cannot move/update card to a column you do not own."
    )