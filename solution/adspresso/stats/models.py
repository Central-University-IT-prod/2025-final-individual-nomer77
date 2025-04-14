from django.db import models


class CampaignDailyStats(models.Model):
    campaign = models.ForeignKey("advertisers.Campaign", on_delete=models.CASCADE, related_name='daily_stats')
    date = models.IntegerField()
    impressions_count = models.IntegerField(default=0)
    clicks_count = models.IntegerField(default=0)
    spent_impressions = models.FloatField(default=0.0)
    spent_clicks = models.FloatField(default=0.0)
    spent_total = models.FloatField(default=0.0)

    @classmethod
    def get_stats_object(cls, campaign_id, date):
        """ Will raise IntegrityError if campaign_id will not exist."""
        obj, created = cls.objects.get_or_create(campaign_id=campaign_id, date=date)
        return obj

    class Meta:
        unique_together = ('campaign', 'date')


class CampaignTotalStats(models.Model):
    campaign = models.OneToOneField("advertisers.Campaign", on_delete=models.CASCADE, related_name='total_stats')
    impressions_count = models.IntegerField(default=0)
    clicks_count = models.IntegerField(default=0)
    spent_impressions = models.FloatField(default=0.0)
    spent_clicks = models.FloatField(default=0.0)
    spent_total = models.FloatField(default=0.0)

    @classmethod
    def get_stats_object(cls, campaign_id):
        """ Will raise IntegrityError if campaign_id will not exist."""
        obj, created = cls.objects.get_or_create(campaign_id=campaign_id)
        return obj
