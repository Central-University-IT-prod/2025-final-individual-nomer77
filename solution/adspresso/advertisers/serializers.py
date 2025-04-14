from rest_framework import serializers
from django.db import IntegrityError

from utils.mixins import RemoveNullableValuesSerializerMixin
from utils.serializers import PositiveIntegerField, PositiveFloatField

from advertisers.models import Advertiser, Campaign
from ads_core.models import AdEngineSettings
from moderation.models import ModerationSettings
from moderation.utils import check_bad_words
from timeline.models import TimeLine


class AdvertiserSerializer(serializers.ModelSerializer):
    advertiser_id = serializers.UUIDField(source='id')
    name = serializers.CharField(max_length=1023)

    class Meta:
        model = Advertiser
        exclude = ('id',)


class TargetingSerializer(
    RemoveNullableValuesSerializerMixin,
    serializers.Serializer,
):
    gender = serializers.ChoiceField(
        source='targeting_gender',
        choices=Campaign.TARGETING_GENDER_CHOICES,
        allow_null=True,
        required=False
    )
    age_from = PositiveIntegerField(
        source="targeting_age_from", allow_null=True, required=False, max_value=128
    )
    age_to = PositiveIntegerField(
        source="targeting_age_to", allow_null=True, required=False, max_value=128
    )
    location = serializers.CharField(
        source="targeting_location", allow_null=True, required=False
    )

    def to_internal_value(self, data):
        if data is None:
            return {}
        return super().to_internal_value(data)

    def validate(self, data):
        age_from = data.get('targeting_age_from')
        age_to = data.get('targeting_age_to')

        if (age_from is not None) and (age_to is not None) and age_from > age_to:
            raise serializers.ValidationError(
                {'ages': 'Age from cannot be greater than age to.'}
            )

        return data


class CampaignSerializer(
    RemoveNullableValuesSerializerMixin,
    serializers.ModelSerializer
):
    targeting = TargetingSerializer(source='*', required=False, allow_null=True)
    advertiser_id = serializers.SerializerMethodField(read_only=True)

    ad_title = serializers.CharField(min_length=3)
    start_date = PositiveIntegerField()
    end_date = PositiveIntegerField()
    impressions_limit = PositiveIntegerField(min_value=1)
    clicks_limit = PositiveIntegerField(min_value=1)
    cost_per_impression = PositiveFloatField()
    cost_per_click = PositiveFloatField()

    disable_to_update_fields = {'campaign_id', 'advertiser_id'}
    disable_to_update_after_start = {
        'impressions_limit', 'clicks_limit', 'start_date', 'end_date'
    }

    @staticmethod
    def get_advertiser_id(obj):
        return obj.advertiser_id

    def get_advertiser_id_by_context(self):
        return self.context['advertiser_id']

    def validate(self, data):
        current_date = TimeLine.get_current_date_object().current_date

        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if current_date > end_date:
            raise serializers.ValidationError(
                {'end_date': 'End date cannot be less than current_date.'}
            )

        if current_date > start_date:
            raise serializers.ValidationError(
                {'start_date': 'Start date cannot be less than current_date.'}
            )

        if start_date > end_date:
            raise serializers.ValidationError(
                {'dates': 'Start date cannot be greater than end date.'}
            )

        if data.get('clicks_limit') > data.get('impressions_limit'):
            raise serializers.ValidationError(
                {'limits': "Click's limit cannot be greater than impression's limit"}
            )

        if (ModerationSettings.get_moderation_settings_object().moderate and
                check_bad_words(data.get('ad_title') + ' ' + data.get('ad_text'))):
            raise serializers.ValidationError(
                {'moderation': "Your ad was rejected due to suspicions of bad words."}
            )

        return data

    def create(self, validated_data):
        try:
            campaign = Campaign.objects.create(
                advertiser_id = self.get_advertiser_id_by_context(),
                **validated_data
            )
        except IntegrityError:
            raise serializers.ValidationError(
                {'advertiser_id': 'Please check that advertiser with this advertiser_id exists.'}
            )

        ad_cost = campaign.cost_per_click + campaign.cost_per_impression
        if ad_cost > AdEngineSettings.get_settings().max_ad_cost:
            AdEngineSettings.update_settings(max_ad_cost=ad_cost)

        return campaign

    def update(self, instance, validated_data):
        updatable_fields = (
            (set(self.Meta.fields) | {field.source for field in self.fields['targeting'].fields.values()}) - self.disable_to_update_fields
        )

        if (instance.start_date >= TimeLine.get_current_date_object().current_date) and (validated_data.keys() & self.disable_to_update_after_start):
            raise serializers.ValidationError(
                {
                    'update_after_start_campaign': f'You cant update fields {validated_data.keys() & self.disable_to_update_after_start} after start the campaign.'
                }
            )


        for field in updatable_fields:
            if field not in validated_data:
                setattr(instance, field, None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    class Meta:
        model = Campaign
        fields = [
            'campaign_id', 'advertiser_id', 'impressions_limit', 'clicks_limit',
            'cost_per_impression', 'cost_per_click', 'ad_title', 'ad_text',
            'start_date', 'end_date', 'targeting', 'image'
        ]
