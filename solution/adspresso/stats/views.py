from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from advertisers.models import Campaign, Advertiser
from stats.models import CampaignDailyStats
from stats.serializers import CampaignDailyStatSerializer, CampaignTotalStatSerializer


class CampaignStatsAPIView(APIView):
    serializer_class = CampaignTotalStatSerializer

    def get(self, request, campaign_id):
        campaign = get_object_or_404(Campaign, campaign_id=campaign_id)

        return Response(
            self.serializer_class(campaign.total_stats).data
        )


class AdvertiserStatsAPIView(APIView):

    @staticmethod
    def get(request, advertiser_id):
        campaigns = Campaign.objects.select_related('total_stats').filter(advertiser_id=advertiser_id)
        stats = campaigns.aggregate(
            impressions_count=Sum('total_stats__impressions_count'),
            clicks_count=Sum('total_stats__clicks_count'),
            spent_impressions=Sum('total_stats__spent_impressions'),
            spent_clicks=Sum('total_stats__spent_clicks'),
            spent_total=Sum('total_stats__spent_total')
        )
        impressions = stats.get('impressions_count') or 0
        clicks = stats.get('clicks_count') or 0
        conversion = (clicks / impressions * 100) if impressions > 0 else 0.0
        return Response(
            data={
                'impressions_count': impressions,
                'clicks_count': clicks,
                'conversion': conversion,
                'spent_impressions': stats.get('spent_impressions') or 0.0,
                'spent_clicks': stats.get('spent_clicks') or 0.0,
                'spent_total': stats.get('spent_total') or 0.0
            },
            status=status.HTTP_200_OK
        )


class CampaignDailyStatsAPIView(APIView):
    serializer_class = CampaignDailyStatSerializer

    def get(self, request, campaign_id):
        campaign = get_object_or_404(Campaign, campaign_id=campaign_id)
        daily_stats = campaign.daily_stats.all().order_by('date')
        return Response(
            self.serializer_class(daily_stats, many=True).data,
            status=status.HTTP_200_OK
        )


class AdvertiserDailyStatsAPIView(APIView):
    serializer_class = CampaignDailyStatSerializer

    def get(self, request, advertiser_id):
        advertiser = get_object_or_404(Advertiser, id=advertiser_id)

        daily_stats = CampaignDailyStats.objects.filter(
            campaign__advertiser=advertiser
        ).order_by('date')

        return Response(
            data=self.serializer_class(daily_stats, many=True).data,
            status=status.HTTP_200_OK
        )
