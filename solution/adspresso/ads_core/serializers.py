from rest_framework import serializers

from advertisers.models import Campaign


class AdForUserSerializer(serializers.ModelSerializer):
    ad_id = serializers.UUIDField(source='campaign_id', read_only=True)

    class Meta:
        model = Campaign
        fields = ('ad_id', 'ad_title', 'ad_text', 'advertiser_id')
