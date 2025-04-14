from django.db import models

from advertisers.models import Advertiser
from clients.models import Client


class MLScore(models.Model):
    client = models.ForeignKey(Client, related_name='ml_score', on_delete=models.CASCADE)
    advertiser = models.ForeignKey(Advertiser, related_name='ml_score', on_delete=models.CASCADE)
    score = models.PositiveIntegerField()

    class Meta:
        unique_together = ('advertiser', 'client', 'score')
