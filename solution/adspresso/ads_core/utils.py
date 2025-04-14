from django.shortcuts import get_object_or_404
from django.db.models import F, ExpressionWrapper, FloatField, Value, Q, BigIntegerField
from django.db.models.functions import Coalesce
from rest_framework import serializers
import uuid

from clients.models import Client
from timeline.models import TimeLine
from advertisers.models import Campaign
from MLScorer.models import MLScore
from ads_core.models import AdEngineSettings

class AdRecommendClass:

    @staticmethod
    def get_client_object(request) -> Client:
        client_id = request.query_params.get('client_id')
        if not client_id:
            raise serializers.ValidationError(
                {'error': 'client_id query parameter is required.'}
            )
        try:
            uuid.UUID(client_id, version=4)
        except ValueError:
            raise serializers.ValidationError(
                {'error': 'client_id must be UUID.'}
            )
        return get_object_or_404(Client, id=client_id)


    @staticmethod
    def get_targeting_filter(client: Client) -> Q:
        filters = Q()

        filters &= (~Q(client_impressions__client=client)) | Q(client_impressions__isnull=True)

        filters &= Q(targeting_location__isnull=True) | Q(targeting_location=client.location)
        filters &= Q(targeting_age_from__isnull=True) | Q(targeting_age_from__lte=client.age)
        filters &= Q(targeting_age_to__isnull=True) | Q(targeting_age_to__gte=client.age)
        filters &= Q(targeting_gender__isnull=True) | Q(targeting_gender=client.gender) | Q(targeting_gender="ALL")

        return filters


    @staticmethod
    def get_active_campaigns_filter(current_date: int) -> Q:
        filters = Q()

        filters &= Q(start_date__lte=current_date, end_date__gte=current_date)
        filters &= Q(total_stats__impressions_count__lt=1.04*F('impressions_limit'))

        return filters


    @classmethod
    def recommend(cls, request):
        client = cls.get_client_object(request)
        current_date = TimeLine.get_current_date_object().current_date

        engine_settings = AdEngineSettings.get_settings()

        max_ad_cost = engine_settings.max_ad_cost
        max_ml_score = engine_settings.max_ml_score

        available_campaign = (Campaign.objects.
            prefetch_related('client_impressions').
            select_related('total_stats').
            filter(
                cls.get_targeting_filter(client) & cls.get_active_campaigns_filter(current_date)
            )
        )

        best_campaign = available_campaign.annotate(

            # Максимальный показатель стоимости за показ и клик
            max_ad_cost=Value(max_ad_cost, output_field=FloatField()),

            # Максимальный показатель совместимости клиента и рекламодателя (нужно для нормализации)
            max_ml_score=Value(max_ml_score, output_field=BigIntegerField()),

            # 1. Нормализованный показатель стоимости за показ и клик
            cost_score=(
                    F('cost_per_impression') + 0.5*F('cost_per_click')
            ),

            # ML-оценка для текущей кампании (если нет записи, то 0)
            ml_score=Coalesce(
                MLScore.objects.filter(advertiser=F('advertiser'), client=client).values('score')[:1],
                Value(0)
            ),

            # 2. Нормализация ML-оценки
            normalized_ml_score=ExpressionWrapper(
                F('ml_score') * (F('max_ad_cost') / F('max_ml_score')),
                output_field=FloatField()
            ),

            # 3. Оценка на основе текущих показателей
            engagement_score=1 - (
                    (F('total_stats__clicks_count') + F('total_stats__impressions_count'))
                    / (F('clicks_limit') + F('impressions_limit')))
        ).annotate(
            # Итоговая аннотированная оценка с учетом весов
            weighted_score=(
                0.7*F('cost_score') +
                0.4*F('normalized_ml_score') +
                0.05*F('engagement_score')
            )
        ).order_by(
            '-weighted_score'  # Сортируем по комбинированному итоговому результату
        ).first()

        return best_campaign, client
