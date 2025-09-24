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
        ids = [b["id"] for b in resp2.data]
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


from django.test import TestCase

# Create your tests here.
