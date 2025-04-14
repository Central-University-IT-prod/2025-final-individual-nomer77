from django.urls import path
from adspresso.routers import NoSlashRouter

from moderation.views import ModerationOnAPIView, ModerationOffAPIView, AddNewWordsAPIView


urlpatterns = [
    path('status/on', ModerationOnAPIView.as_view()),
    path('status/off', ModerationOffAPIView.as_view()),
    path('words', AddNewWordsAPIView.as_view()),
]
