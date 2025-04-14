import uuid
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from advertisers.models import Advertiser


@pytest.mark.django_db
class TestBulkCreateUpdateAdvertiser(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/advertisers/bulk"
        self.existing_advertiser = Advertiser.objects.create(
            id=uuid.uuid4(), name="existing_advertiser"
        )

    def test_bulk_create_success(self):
        """Тест успешного массового создания рекламодателей"""
        new_advertisers = [
            {
                "advertiser_id": str(uuid.uuid4()),
                "name": "new_advertiser_1"
            },
            {
                "advertiser_id": str(uuid.uuid4()),
                "name": "new_advertiser_2"
            },
        ]

        response = self.client.post(self.url, data=new_advertisers, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Advertiser.objects.count() == 3  # 2 новых + 1 существующий

    def test_bulk_update_success(self):
        """Тест успешного массового обновления рекламодателей"""
        update_data = [
            {
                "advertiser_id": str(self.existing_advertiser.id),
                "name": "updated_advertiser"
            }
        ]

        response = self.client.post(self.url, data=update_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        self.existing_advertiser.refresh_from_db()
        assert self.existing_advertiser.name == "updated_advertiser"


    def test_bulk_create_and_update_mixed(self):
        """Тест обновления существующего рекламодателя и создания нового"""
        new_id = str(uuid.uuid4())
        data = [
            {
                "advertiser_id": str(self.existing_advertiser.id),
                "name": "updated_existing",
            },
            {
                "advertiser_id": new_id,
                "name": "new_advertiser",
            },
        ]

        response = self.client.post(self.url, data=data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        self.existing_advertiser.refresh_from_db()
        assert self.existing_advertiser.name == "updated_existing"
        assert Advertiser.objects.filter(id=new_id).exists()

    def test_bulk_invalid_uuid(self):
        """Тест ошибки при передаче неверного UUID"""
        invalid_data = [{"advertiser_id": "invalid_uuid", "name": "fake_name"}]

        response = self.client.post(self.url, data=invalid_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_missing_id(self):
        """Тест ошибки при отсутствии 'advertiser_id'"""
        missing_id_data = [{"name": "fake_name"}]

        response = self.client.post(self.url, data=missing_id_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_duplicate_ids(self):
        """Тест ошибки при дублирующихся ID в запросе"""
        duplicate_id = str(uuid.uuid4())
        duplicate_data = [
            {"advertiser_id": duplicate_id, "name": "advertiser1"},
            {"advertiser_id": duplicate_id, "name": "advertiser1"},
        ]

        response = self.client.post(self.url, data=duplicate_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
