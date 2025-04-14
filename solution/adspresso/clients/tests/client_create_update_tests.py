import uuid
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from clients.models import Client


@pytest.mark.django_db
class TestBulkCreateUpdateClient(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/clients/bulk"
        self.existing_client = Client.objects.create(
            id=uuid.uuid4(), login="existing_user", age=30, location="NY", gender="MALE"
        )

    def test_bulk_create_success(self):
        """Тест успешного массового создания клиентов"""
        new_clients = [
            {
                "client_id": str(uuid.uuid4()),
                "login": "new_user_1",
                "age": 25,
                "location": "LA",
                "gender": "FEMALE",
            },
            {
                "client_id": str(uuid.uuid4()),
                "login": "new_user_2",
                "age": 28,
                "location": "SF",
                "gender": "MALE",
            },
        ]

        response = self.client.post(self.url, data=new_clients, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Client.objects.count() == 3  # 2 новых + 1 существующий

    def test_bulk_update_success(self):
        """Тест успешного массового обновления клиентов"""
        update_data = [
            {
                "client_id": str(self.existing_client.id),
                "login": "updated_user",
                "age": 35,
                "location": "NYC",
                "gender": "MALE",
            }
        ]

        response = self.client.post(self.url, data=update_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        self.existing_client.refresh_from_db()
        assert self.existing_client.login == "updated_user"
        assert self.existing_client.age == 35

    def test_bulk_create_and_update_mixed(self):
        """Тест обновления существующего клиента и создания нового"""
        new_id = str(uuid.uuid4())
        data = [
            {
                "client_id": str(self.existing_client.id),
                "login": "updated_existing",
                "age": 40,
                "location": "London",
                "gender": "MALE",
            },
            {
                "client_id": new_id,
                "login": "new_user",
                "age": 22,
                "location": "Berlin",
                "gender": "FEMALE",
            },
        ]

        response = self.client.post(self.url, data=data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        self.existing_client.refresh_from_db()
        assert self.existing_client.login == "updated_existing"
        assert Client.objects.filter(id=new_id).exists()

    def test_bulk_invalid_uuid(self):
        """Тест ошибки при передаче неверного UUID"""
        invalid_data = [{"client_id": "invalid_uuid", "login": "user", "age": 23, "location": "LA", "gender": "MALE"}]

        response = self.client.post(self.url, data=invalid_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_missing_id(self):
        """Тест ошибки при отсутствии 'client_id'"""
        missing_id_data = [{"login": "user", "age": 23, "location": "LA", "gender": "MALE"}]

        response = self.client.post(self.url, data=missing_id_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_duplicate_ids(self):
        """Тест ошибки при дублирующихся ID в запросе"""
        duplicate_id = str(uuid.uuid4())
        duplicate_data = [
            {"client_id": duplicate_id, "login": "user1", "age": 20, "location": "Paris", "gender": "MALE"},
            {"client_id": duplicate_id, "login": "user2", "age": 21, "location": "Berlin", "gender": "FEMALE"},
        ]

        response = self.client.post(self.url, data=duplicate_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
