from django.db import models
from django_minio_backend import MinioBackend
import uuid

from utils.manager import AdspressoManager

from clients.models import Client
from stats.models import CampaignTotalStats


class Advertiser(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False)
    name = models.CharField(max_length=1023)

    objects = AdspressoManager()

    conflict_fields = ('id',)
    update_fields = ('name',)


def campaign_image_upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)


class Campaign(models.Model):
    TARGETING_GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('ALL', 'All')
    )

    campaign_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE, related_name='campaigns')
    image = models.ImageField(
        storage=MinioBackend(bucket_name='adspresso-campaigns'),
        upload_to=campaign_image_upload_to,
        null=True,
        blank=True
    )
    impressions_limit = models.IntegerField()
    clicks_limit = models.IntegerField()
    cost_per_impression = models.FloatField()
    cost_per_click = models.FloatField()
    ad_title = models.CharField(max_length=255)
    ad_text = models.TextField()
    start_date = models.IntegerField()  # Current day as an integer
    end_date = models.IntegerField()

    targeting_gender = models.CharField(max_length=6, choices=TARGETING_GENDER_CHOICES, null=True, blank=True)
    targeting_age_from = models.IntegerField(null=True, blank=True)
    targeting_age_to = models.IntegerField(null=True, blank=True)
    targeting_location = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        created = self._state.adding
        super().save(*args, **kwargs)
        if created:
            CampaignTotalStats.objects.create(campaign=self)
