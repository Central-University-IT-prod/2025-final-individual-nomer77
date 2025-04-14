from rest_framework import serializers


class PositiveIntegerField(serializers.IntegerField):
    def __init__(self, **kwargs):
        kwargs.setdefault('min_value', 0)
        super().__init__(**kwargs)


class PositiveFloatField(serializers.FloatField):
    def __init__(self, **kwargs):
        kwargs.setdefault('min_value', 0.0)
        super().__init__(**kwargs)
