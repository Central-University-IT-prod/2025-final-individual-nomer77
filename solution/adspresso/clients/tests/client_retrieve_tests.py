import uuid
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from clients.models import Client


@pytest.mark.django_db
class TestClientRetrieve(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/clients/{client_id}"


    def test_retrieve_existing_client(self):
        """Проверяет получение существующего клиента по ID"""
        client = Client.objects.create(
            id=uuid.uuid4(),
            login="test_user",
            age=25,
            location="New York",
            gender="MALE"
        )

        response = self.client.get(self.url.format(client_id=client.id))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["client_id"] == str(client.id)
        assert response.data["login"] == "test_user"
        assert response.data["age"] == 25
        assert response.data["location"] == "New York"
        assert response.data["gender"] == "MALE"

    def test_retrieve_non_existent_client(self):
        """Проверяет, что запрос на несуществующего клиента вернёт 404"""
        non_existent_id = uuid.uuid4()
        response = self.client.get(self.url.format(client_id=non_existent_id))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_invalid_uuid(self):
        """Проверяет, что если передать невалидный UUID, сервер вернёт 404, а не 500"""
        invalid_uuid = "invalid-uuid"
        response = self.client.get(self.url.format(client_id=invalid_uuid))

        assert response.status_code == status.HTTP_404_NOT_FOUND