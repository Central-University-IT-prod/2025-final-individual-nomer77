from rest_framework import serializers
from django.db import IntegrityError

from MLScorer.models import MLScore
from ads_core.models import AdEngineSettings


class MLScoreSerializer(serializers.ModelSerializer):
    client_id = serializers.UUIDField(source='client.id')
    advertiser_id = serializers.UUIDField(source='advertiser.id')
    score = serializers.IntegerField(min_value=0)

    class Meta:
        model = MLScore
        fields = ('client_id', 'advertiser_id', 'score')

    def create(self, validated_data):
        try:
            obj, created = MLScore.objects.update_or_create(
                client_id=validated_data.get('client')['id'],
                advertiser_id=validated_data.get('advertiser')['id'],
                score=validated_data.get('score')
            )

            if obj.score > AdEngineSettings.get_settings().max_ml_score:
                AdEngineSettings.update_settings(max_ml_score=obj.score)

        except IntegrityError:
            raise serializers.ValidationError(
                {'error': "Please check that client_id and advertiser_id exists"}
            )
        return obj