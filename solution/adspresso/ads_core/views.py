from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
import uuid

from timeline.models import TimeLine
from clients.models import Client
from advertisers.models import Campaign
from stats.models import CampaignDailyStats
from ads_core.serializers import AdForUserSerializer
from ads_core.utils import AdRecommendClass

class AdForClientAPIView(APIView):

    @staticmethod
    def get(request):
        best_campaign, client = AdRecommendClass.recommend(request)

        if best_campaign is None:
            return Response(
                data={'detail': 'You are free! No ads.'},
                status=status.HTTP_404_NOT_FOUND
            )

        with transaction.atomic():
            advertiser_paid = best_campaign.cost_per_impression

            best_campaign.total_stats.impressions_count += 1
            best_campaign.total_stats.spent_impressions += advertiser_paid
            best_campaign.total_stats.spent_total += advertiser_paid

            daily_stat_object = CampaignDailyStats.get_stats_object(
                campaign_id=best_campaign.campaign_id,
                date=TimeLine.get_current_date_object().current_date
            )
            daily_stat_object.impressions_count += 1
            daily_stat_object.spent_impressions += advertiser_paid
            daily_stat_object.spent_total += advertiser_paid

            client.ad_impressions.create(
                campaign=best_campaign,
                date=TimeLine.get_current_date_object().current_date
            )
            client.impressions_count += 1

            daily_stat_object.save()
            best_campaign.total_stats.save()
            client.save()

        return Response(
            data=AdForUserSerializer(best_campaign).data,
            status=status.HTTP_200_OK
        )


class AdClickAPIView(APIView):

    @staticmethod
    def get_client_id(request):
        client_id = request.data.get('client_id')
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
        return client_id

    def post(self, request, ad_id):
        client_id = self.get_client_id(request)

        client = get_object_or_404(Client, id=client_id)
        campaign = get_object_or_404(Campaign, campaign_id=ad_id)

        if client.ad_clicks.filter(campaign=campaign).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)

        with transaction.atomic():
            advertiser_paid = campaign.cost_per_click

            client.ad_clicks.create(
                campaign=campaign,
                date=TimeLine.get_current_date_object().current_date
            )
            client.clicks_count += 1

            campaign.total_stats.clicks_count += 1
            campaign.total_stats.spent_clicks += advertiser_paid
            campaign.total_stats.spent_total += advertiser_paid

            daily_stat_object = CampaignDailyStats.get_stats_object(
                campaign_id=campaign.campaign_id,
                date=TimeLine.get_current_date_object().current_date
            )
            daily_stat_object.clicks_count += 1
            daily_stat_object.spent_clicks += advertiser_paid
            daily_stat_object.spent_total += advertiser_paid

            daily_stat_object.save()
            campaign.total_stats.save()
            client.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
