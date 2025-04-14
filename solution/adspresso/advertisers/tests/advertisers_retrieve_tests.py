import uuid
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from advertisers.models import Advertiser


@pytest.mark.django_db
class TestAdvertiserRetrieve(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/advertisers/{advertiser_id}"

    def test_retrieve_existing_client(self):
        """Проверяет получение существующего рекламодателей по ID"""
        advertiser = Advertiser.objects.create(
            id=uuid.uuid4(),
            name="test_advertiser"
        )

        response = self.client.get(self.url.format(advertiser_id=advertiser.id))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["advertiser_id"] == str(advertiser.id)
        assert response.data["name"] == "test_advertiser"

    def test_retrieve_non_existent_client(self):
        """Проверяет, что запрос на несуществующего рекламодателя вернёт 404"""
        non_existent_id = uuid.uuid4()
        response = self.client.get(self.url.format(advertiser_id=non_existent_id))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_invalid_uuid(self):
        """Проверяет, что если передать невалидный UUID, сервер вернёт 404, а не 500"""
        invalid_uuid = "invalid-uuid"
        response = self.client.get(self.url.format(advertiser_id=invalid_uuid))

        assert response.status_code == status.HTTP_404_NOT_FOUND