from django.db import models
from utils.manager import AdspressoManager


class Client(models.Model):
    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
    )

    id = models.UUIDField(primary_key=True, unique=True, editable=False)
    login = models.CharField(max_length=255)
    age = models.SmallIntegerField()
    location = models.CharField(max_length=255)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)

    impressions_count = models.PositiveIntegerField(default=0)
    clicks_count = models.PositiveIntegerField(default=0)

    objects = AdspressoManager()

    conflict_fields = ('id',)
    update_fields = ('login', 'age', 'location', 'gender')
