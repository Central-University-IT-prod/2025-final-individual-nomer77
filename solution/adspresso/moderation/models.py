from django.db import models
from django.core.cache import cache


class ModerationSettings(models.Model):
    moderate = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.set("moderation:moderate", self.moderate)

    @classmethod
    def get_moderation_settings_object(cls):
        state = cache.get("moderation:moderate")
        if state is not None:
            return cls(pk=1, moderate=state)

        obj, created = cls.objects.get_or_create(pk=1)
        cache.set("moderation:moderate", obj.moderate)
        return obj


class BlackWord(models.Model):
    word = models.CharField(max_length=127)

    def __str__(self):
        return self.word
