from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Card, Column, Board
from .serializers import CardSerializer, ColumnSerializer, BoardSerializer


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ColumnViewSet(viewsets.ModelViewSet):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(board__owner=self.request.user)

    def perform_create(self, serializer):
        board = serializer.validated_data.get("board")
        if board.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Cannot create column on a board you do not own.")
        serializer.save()

    def perform_update(self, serializer):
        board = serializer.validated_data.get(
            "board", getattr(serializer.instance, "board", None)
        )
        if board and board.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Cannot move/update column to a board you do not own."
            )
        serializer.save()


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(column__board__owner=self.request.user)

    def perform_create(self, serializer):
        column = serializer.validated_data.get("column")
        if column.board.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Cannot create card inside a column you do not own.")
        serializer.save()

    def perform_update(self, serializer):
        column = serializer.validated_data.get(
            "column", getattr(serializer.instance, "column", None)
        )
        if column and column.board.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Cannot move/update card to a column you do not own."
            )
        serializer.save()
