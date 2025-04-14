from rest_framework import mixins, status
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import get_object_or_404
from gigachat import GigaChat

from utils.mixins import BulkUpdateOrCreateViewsMixin
from utils.pagination import HeaderLimitOffsetPagination

from advertisers.models import Advertiser, Campaign
from advertisers.serializers import AdvertiserSerializer, CampaignSerializer


class AdvertiserViewSet(
    mixins.RetrieveModelMixin,
    BulkUpdateOrCreateViewsMixin,
    GenericViewSet
):
    model = Advertiser
    queryset = Advertiser.objects.all()
    serializer_class = AdvertiserSerializer
    pk_field_name = "advertiser_id"


class CampaignViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    model = Campaign
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    pagination_class = HeaderLimitOffsetPagination

    def get_advertiser_id(self):
        return self.kwargs.get('advertiser_id')

    def get_serializer_context(self):
        return {'advertiser_id': self.get_advertiser_id()}

    def get_queryset(self):
        return super().get_queryset().filter(advertiser_id=self.get_advertiser_id())


class LLMAPIView(APIView):

    @staticmethod
    def post(request, advertiser_id):
        ad_title = request.data.get('ad_title')
        if ad_title is None:
            return Response(
                data={'error': 'ad_title is required field.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        advertiser = get_object_or_404(Advertiser, id=advertiser_id)

        with GigaChat(credentials=settings.LLM_AUTH_KEY, verify_ssl_certs=False) as giga:
            response = giga.chat(f"Для рекламодателя '{advertiser.name}' придумай текст рекламного объявление с названием {ad_title}")
            text = response.choices[0].message.content

        return Response(
            data={'ad_text': text},
            status=status.HTTP_200_OK
        )