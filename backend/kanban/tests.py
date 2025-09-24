from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from common.enums.errors import ErrorEnum


User = get_user_model()


class KanbanAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="kbuser", password="P@ssw0rd123")
        # obtain token via the auth endpoints
        token_url = reverse("token_obtain_pair")
        resp = self.client.post(
            token_url, {"username": "kbuser", "password": "P@ssw0rd123"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.access = resp.data.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    def test_board_create_list_and_owner_filtering(self):
        board_url = reverse("board-list")
        data = {"title": "Test Board", "description": "desc"}
        resp = self.client.post(board_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        board_id = resp.data.get("id")

        # list should include created board
        resp2 = self.client.get(board_url)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        data = resp2.data
        # if pagination is enabled, results will be present
        if isinstance(data, dict) and "results" in data:
            items = data["results"]
        else:
            items = data
        ids = [b["id"] for b in items]
        self.assertIn(board_id, ids)

    def test_column_and_card_crud_and_scope(self):
        # create board
        board = self.client.post(
            reverse("board-list"), {"title": "B1"}, format="json"
        ).data
        board_id = board["id"]

        # create column
        col = self.client.post(
            reverse("column-list"),
            {"title": "ToDo", "board": board_id, "position": 1},
            format="json",
        )
        self.assertEqual(col.status_code, status.HTTP_201_CREATED)
        col_id = col.data.get("id")

        # create card with valid priority
        card_resp = self.client.post(
            reverse("card-list"),
            {"title": "C1", "column": col_id, "position": 1, "priority": "high"},
            format="json",
        )
        self.assertEqual(card_resp.status_code, status.HTTP_201_CREATED)

        # create card with invalid priority
        bad = self.client.post(
            reverse("card-list"),
            {"title": "C2", "column": col_id, "position": 2, "priority": "super"},
            format="json",
        )
        self.assertEqual(bad.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("priority", bad.data)
        # depending on whether model choice validation or serializer validate_priority
        # runs first, the message may be the custom ErrorEnum or the DRF default.
        msg = str(bad.data.get("priority"))
        self.assertTrue(
            ErrorEnum.INVALID_PRIORITY.value in msg or "not a valid choice" in msg
        )

    def test_cannot_create_column_or_card_on_another_users_board(self):
        # create a board as first user
        board = self.client.post(
            reverse("board-list"), {"title": "OwnerBoard"}, format="json"
        ).data
        board_id = board["id"]

        # create second user and token
        other = User.objects.create_user(username="other", password="P@ssw0rd456")
        token_url = reverse("token_obtain_pair")
        resp = APIClient().post(
            token_url, {"username": "other", "password": "P@ssw0rd456"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        other_access = resp.data.get("access")

        client2 = APIClient()
        client2.credentials(HTTP_AUTHORIZATION=f"Bearer {other_access}")

        # other user should NOT be able to create a column on first user's board
        col_resp = client2.post(
            reverse("column-list"),
            {"title": "X", "board": board_id, "position": 1},
            format="json",
        )
        self.assertIn(
            col_resp.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST),
        )

        # Similarly cannot create a card inside a column owned by first user
        # Create a column as owner
        col = self.client.post(
            reverse("column-list"),
            {"title": "OwnerCol", "board": board_id, "position": 1},
            format="json",
        ).data
        col_id = col["id"]

        card_resp = client2.post(
            reverse("card-list"),
            {"title": "BadCard", "column": col_id, "position": 1, "priority": "low"},
            format="json",
        )
        self.assertIn(
            card_resp.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST),
        )


from django.test import TestCase

# Create your tests here.
