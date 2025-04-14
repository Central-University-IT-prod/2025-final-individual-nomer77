from django.urls import path
from stats.views import (
    CampaignStatsAPIView,
    CampaignDailyStatsAPIView,
    AdvertiserStatsAPIView,
    AdvertiserDailyStatsAPIView
)


urlpatterns = [
    path('campaigns/<uuid:campaign_id>', CampaignStatsAPIView.as_view(), name='get_campaign_stats'),
    path('advertisers/<uuid:advertiser_id>/campaigns', AdvertiserStatsAPIView.as_view(), name='get_advertiser_campaigns_stats'),
    path('campaigns/<uuid:campaign_id>/daily', CampaignDailyStatsAPIView.as_view(), name='get_campaign_daily_stats'),
    path('advertisers/<uuid:advertiser_id>/campaigns/daily', AdvertiserDailyStatsAPIView.as_view(), name='get_advertiser_daily_stats'),
]
