from django.db import models
from django.core.cache import cache


class TimeLine(models.Model):
    current_date = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.set("timeline:current_date", self.current_date)

    @classmethod
    def get_current_date_object(cls):
        current_date = cache.get("timeline:current_date")
        if current_date is not None:
            obj = cls(pk=1, current_date=int(current_date))
            return obj

        obj, created = cls.objects.get_or_create(pk=1, defaults={'current_date': 0})
        cache.set("timeline:current_date", obj.current_date)
        return obj
