import uuid

from django.test import TestCase
import pytest
from rest_framework.exceptions import ValidationError
from django.db.utils import IntegrityError
from MLScorer.models import MLScore, Client, Advertiser
from MLScorer.serializers import MLScoreSerializer
from ads_core.models import AdEngineSettings


@pytest.mark.django_db
class TestMlScoreSerializer(TestCase):
    def setUp(self):
        self.existing_client = Client.objects.create(
            id="024e545c-7f4c-471c-a3ea-39063fa31019",
            login="yTH8eLXG3J@yandex.ru",
            age=35,
            location="Miami",
            gender="FEMALE"
        )
        self.existing_advertiser = Advertiser.objects.create(
            id="2a51ba38-bed3-43af-bbb4-99093b72e0d1",
            name="Advertiser 1"
        )

    def test_ml_score_serializer_valid_data(self,):
        """Создание валидного ml-score"""
        data = {
            'client_id': self.existing_client.id,
            'advertiser_id': self.existing_advertiser.id,
            'score': 85
        }
        serializer = MLScoreSerializer(data=data)

        assert serializer.is_valid()

        obj = serializer.save()
        assert str(obj.client.id) == str(self.existing_client.id)
        assert str(obj.advertiser.id) == str(self.existing_advertiser.id)
        assert obj.score == 85



    def test_ml_score_serializer_score_over_max_ml_score(self):
        """ Проверяем, что максимальный ml-score в настройках обновился"""
        AdEngineSettings.objects.create(max_ml_score=100)

        data = {
            'client_id': self.existing_client.id,
            'advertiser_id': self.existing_advertiser.id,
            'score': 105  # Слишком высокий балл
        }

        serializer = MLScoreSerializer(data=data)

        assert serializer.is_valid()

        obj = serializer.save()
        assert obj.score == 105
        assert AdEngineSettings.objects.first().max_ml_score == 105


    def test_ml_score_serializer_invalid_data(self):
        """ Попробуем создать объект с некорректными данными (например, невалидные client_id или advertiser_id) """
        data = {
            'client_id': 'sdf',
            'advertiser_id': uuid.uuid4(),
            'score': 85
        }

        serializer = MLScoreSerializer(data=data)

        assert not serializer.is_valid()
