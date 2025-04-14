from rest_framework import serializers

from stats.models import CampaignDailyStats, CampaignTotalStats


class CampaignDailyStatSerializer(serializers.ModelSerializer):
    conversion = serializers.SerializerMethodField()

    @staticmethod
    def get_conversion(obj):
        if obj.impressions_count == 0:
            return 0.0
        return round(
            (obj.clicks_count / obj.impressions_count) * 100,
            ndigits=2
        )

    class Meta:
        model = CampaignDailyStats
        fields = (
            'impressions_count', 'clicks_count', 'conversion',
            'spent_impressions', 'spent_clicks', 'spent_total',
            'date'
        )


class CampaignTotalStatSerializer(serializers.ModelSerializer):
    conversion = serializers.SerializerMethodField()

    @staticmethod
    def get_conversion(obj):
        if obj.impressions_count == 0:
            return 0.0
        return round(
            (obj.clicks_count / obj.impressions_count) * 100,
            ndigits=2
        )

    class Meta:
        model = CampaignTotalStats
        fields = (
            'impressions_count', 'clicks_count', 'conversion',
            'spent_impressions', 'spent_clicks', 'spent_total'
        )
