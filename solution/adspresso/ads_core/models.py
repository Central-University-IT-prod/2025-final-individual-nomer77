from django.db import models
from django.core.cache import cache

from clients.models import Client
from advertisers.models import Campaign


class ClientImpressionAd(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="ad_impressions")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="client_impressions")
    date = models.PositiveBigIntegerField()

    class Meta:
        unique_together = ("client", "campaign")


class ClientClickAd(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="ad_clicks")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="client_clicks")
    date = models.PositiveBigIntegerField()

    class Meta:
        unique_together = ("client", "campaign")


class AdEngineSettings(models.Model):
    max_ad_cost = models.FloatField(default=-1.0) # Чтобы цена любой новой рекламы была больше этого значения
    max_ml_score = models.BigIntegerField(default=1)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.set("ad_engine_settings:max_ad_cost", self.max_ad_cost)
        cache.set("ad_engine_settings:max_ml_score", self.max_ml_score)

    @classmethod
    def get_settings(cls):
        max_ad_cost = cache.get("ad_engine_settings:max_ad_cost")
        max_ml_score = cache.get("ad_engine_settings:max_ml_score")
        if (max_ad_cost is not None) and (max_ml_score is not None):
            obj = cls(
                pk=1, max_ad_cost=int(max_ad_cost), max_ml_score=int(max_ml_score)
            )
            return obj

        settings, created = cls.objects.get_or_create(id=1)

        cache.set("ad_engine_settings:max_ad_cost", settings.max_ad_cost)
        cache.set("ad_engine_settings:max_ml_score", settings.max_ml_score)

        return settings

    @classmethod
    def update_settings(cls, max_ad_cost=None, max_ml_score=None):

        settings = cls.get_settings()
        if max_ad_cost is not None:
            settings.max_ad_cost = max_ad_cost
        if max_ml_score is not None:
            settings.max_ml_score = max_ml_score
        settings.save()
