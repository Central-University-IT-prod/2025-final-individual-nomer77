from django.http import JsonResponse
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from MLScorer.views import MLScoreAPIView
from timeline.views import AdvanceTime
from ads_core.views import AdForClientAPIView, AdClickAPIView


schema_view = get_schema_view(
   openapi.Info(
      title="Adspresso API",
      default_version='v1',
      description="Individual Final of PROD 2025. Ivan Golyshev 'Adspresso'",
   ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),

    path('health/', health_check),

    path('clients/', include(('clients.urls', 'clients'), namespace='clients')),
    path('advertisers/', include(('advertisers.urls', 'advertisers'), namespace='advertisers')),
    path('ml-scores', MLScoreAPIView.as_view(), name='update-ml-score'),
    path('time/advance', AdvanceTime.as_view(), name='advance_day'),

    path('ads', AdForClientAPIView.as_view(), name='get-ads'),
    path('ads/<uuid:ad_id>/click', AdClickAPIView.as_view(), name='ad-click'),

    path('stats/', include(('stats.urls', 'stats'), namespace='stats')),
    path('moderation/', include(('moderation.urls', 'moderation'), namespace='moderation'))
]
