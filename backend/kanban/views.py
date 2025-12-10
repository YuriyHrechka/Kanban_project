from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Card, Column, Board
from .serializers import (
    BoardDetailSerializer,
    CardSerializer,
    ColumnDetailSerializer,
    ColumnSerializer,
    BoardSerializer,
)
from common.enums.errors import ErrorEnum
from rest_framework.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F


class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Board objects.

    - Restricts access to authenticated users only.
    - Each user can only access their own boards.
    """

    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return boards owned by the authenticated user.

        :return: Queryset of boards belonging to the current user.
        """
        return Board.objects.filter(owner=self.request.user).prefetch_related(
            "columns__cards"
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BoardDetailSerializer
        return BoardSerializer

    def perform_create(self, serializer):
        """
        Save a new board with the authenticated user as owner.

        :param serializer: Board serializer instance.
        """
        serializer.save(owner=self.request.user)


class ColumnViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Column objects.

    - Restricts access to authenticated users only.
    - A user can only access columns of boards they own.
    - Prevents creating or moving columns to another user's board.
    """

    queryset = Column.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return columns belonging to the boards owned by the user.

        :return: Queryset of columns for the current user.
        """

        return self.queryset.filter(board__owner=self.request.user).prefetch_related(
            "cards"
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ColumnDetailSerializer
        return ColumnSerializer

    def perform_create(self, serializer):
        """
        Save a new column ensuring the board belongs to the user.

        :param serializer: Column serializer instance.
        :raises PermissionDenied: If user tries to create column on another user's board.
        """
        board = serializer.validated_data.get("board")
        if board.owner != self.request.user:
            raise PermissionDenied(
                ErrorEnum.CANNOT_CREATE_COLUMN_ON_ANOTHER_USERS_BOARD.value
            )
        serializer.save()

    def perform_update(self, serializer):
        """
        Update an existing column ensuring it stays within the user's board.

        :param serializer: Column serializer instance.
        :raises PermissionDenied: If user tries to move column to another user's board.
        """
        board = serializer.validated_data.get(
            "board", getattr(serializer.instance, "board", None)
        )
        if board and board.owner != self.request.user:
            raise PermissionDenied(
                ErrorEnum.CANNOT_MOVE_UPDATE_COLUMN_TO_ANOTHER_USERS_BOARD.value
            )
        serializer.save()

    @action(detail=True, methods=["post"])
    def move(self, request, pk=None):
        """
        Move a column only within its current board.
        Expects payload: {"position": <int>}
        """
        column = self.get_object()
        source_board = column.board

        raw_pos = request.data.get("position")
        try:
            position = int(raw_pos)
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid or missing 'position' (must be integer)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if position < 0:
            return Response(
                {"detail": "'position' must be >= 0."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            qs = Column.objects.select_for_update().filter(board=source_board)

            old_pos = column.position
            total = qs.count()

            if total <= 0:
                position = 0
            else:
                if position > total - 1:
                    position = total - 1

            if position == old_pos:
                serializer = ColumnDetailSerializer(
                    column, context={"request": request}
                )
                return Response(serializer.data, status=status.HTTP_200_OK)

            if position > old_pos:
                qs.filter(position__gt=old_pos, position__lte=position).update(
                    position=F("position") - 1
                )
            else:
                qs.filter(position__gte=position, position__lt=old_pos).update(
                    position=F("position") + 1
                )

            column.position = position
            column.save()

        serializer = ColumnDetailSerializer(column, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Card objects.

    - Restricts access to authenticated users only.
    - A user can only access cards in columns that belong to their boards.
    - Prevents creating or moving cards to another user's column.
    """

    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return cards belonging to columns of the user's boards.

        :return: Queryset of cards for the current user.
        """
        return self.queryset.filter(column__board__owner=self.request.user)

    def perform_create(self, serializer):
        """
        Save a new card ensuring the column belongs to the user's board.

        :param serializer: Card serializer instance.
        :raises PermissionDenied: If user tries to create card in another user's column.
        """
        column = serializer.validated_data.get("column")
        if column.board.owner != self.request.user:
            raise PermissionDenied(
                ErrorEnum.CANNOT_CREATE_CARD_ON_ANOTHER_USERS_COLUMN.value
            )
        serializer.save()

    def perform_update(self, serializer):
        """
        Update an existing card ensuring it stays within the user's column.

        :param serializer: Card serializer instance.
        :raises PermissionDenied: If user tries to move card to another user's column.
        """
        column = serializer.validated_data.get(
            "column", getattr(serializer.instance, "column", None)
        )
        if column and column.board.owner != self.request.user:
            raise PermissionDenied(
                ErrorEnum.CANNOT_MOVE_UPDATE_CARD_TO_ANOTHER_USERS_COLUMN.value
            )
        serializer.save()

    @action(detail=True, methods=["post"])
    def move(self, request, pk=None):
        """
        Move a card to another column and/or update its position.

        :param request: The HTTP request containing JSON body with
                        `"column"` (column id) and `"position"` (integer).
        :param pk: The primary key of the card being moved.

        :return: A Response containing the updated serialized card data,
                or an error message if validation fails.
        """
        card = self.get_object()
        column_id = request.data.get("column")
        position = request.data.get("position")

        if column_id is None:
            return Response(
                {"detail": "column is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            target_column = Column.objects.get(pk=column_id)
        except Column.DoesNotExist:
            return Response(
                {"detail": "target column not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if target_column.board.owner != request.user:
            raise PermissionDenied(
                ErrorEnum.CANNOT_MOVE_UPDATE_CARD_TO_ANOTHER_USERS_COLUMN.value
            )

        card.column = target_column
        if position is not None:
            try:
                card.position = int(position)
            except (TypeError, ValueError):
                return Response(
                    {"detail": "invalid position"}, status=status.HTTP_400_BAD_REQUEST
                )

        card.save()
        serializer = self.get_serializer(card)
        return Response(serializer.data)
