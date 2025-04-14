import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
class TestTimelineViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/time/advance"

    def test_set_valid_str_time(self):
        """Проверяет, что запрос с валидной датой вернет 200"""
        data = {'current_date': 7}
        response = self.client.post(self.url, data=data)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == data

    def test_without_date(self):
        """Проверяет, что запрос без current_date вернет 400"""
        data = {'some_date': 1}
        response = self.client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_with_negative_date(self):
        """Проверяет, что запрос с отрицательным current_date вернет 400"""
        data = {'current_date': -7}
        response = self.client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_with_not_digits_date(self):
        """Проверяет, что запрос с не числовым current_date вернет 400"""
        data = {'current_date': 'abc'}
        response = self.client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST