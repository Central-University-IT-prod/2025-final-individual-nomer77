from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from utils.mixins import BulkUpdateOrCreateViewsMixin

from clients.models import Client
from clients.serializers import ClientSerializer


class ClientViewSet(
    mixins.RetrieveModelMixin,
    BulkUpdateOrCreateViewsMixin,
    GenericViewSet
):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    model = Client
    pk_field_name = "client_id"
    can_be_updated_fields = ('login', 'age', 'location', 'gender')
