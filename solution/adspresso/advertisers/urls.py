from django.urls import path
from adspresso.routers import NoSlashRouter

from advertisers.views import AdvertiserViewSet, CampaignViewSet, LLMAPIView


router = NoSlashRouter()
router.register('', AdvertiserViewSet, basename='advertisers')

urlpatterns = [
    path('<uuid:advertiser_id>/campaigns', CampaignViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('<uuid:advertiser_id>/campaigns/<uuid:pk>',
         CampaignViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('<uuid:advertiser_id>/generate-ad-text', LLMAPIView.as_view()),

]

urlpatterns += router.urls