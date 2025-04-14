from rest_framework import serializers

from utils.serializers import PositiveIntegerField

from clients.models import Client


class ClientSerializer(
    serializers.ModelSerializer
):
    client_id = serializers.UUIDField(source='id')
    age = PositiveIntegerField(max_value=128)


    class Meta:
        model = Client
        fields = ('client_id', 'login', 'age', 'location', 'gender')
