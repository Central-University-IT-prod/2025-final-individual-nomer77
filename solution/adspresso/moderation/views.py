from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from moderation.models import ModerationSettings, BlackWord
from moderation.utils import normalize_word


class ModerationOnAPIView(APIView):
    @staticmethod
    def post(request):
        obj = ModerationSettings.get_moderation_settings_object()
        obj.moderate = True
        obj.save()
        return Response(
            data={'detail': 'Moderation was enabled.'},
            status=status.HTTP_200_OK
        )


class ModerationOffAPIView(APIView):
    @staticmethod
    def post(request):
        obj = ModerationSettings.get_moderation_settings_object()
        obj.moderate = False
        obj.save()
        return Response(
            data={'detail': 'Moderation was disabled.'},
            status=status.HTTP_200_OK
        )


class AddNewWordsAPIView(APIView):
    @staticmethod
    def post(request):
        words = request.data.get('words')
        if words is None:
            return Response(
                data={'error': 'words is required field.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not isinstance(words, list):
            return Response(
                data={'error': 'words must be a list of ban words.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        normalized_word_obj = []
        for word in words:
            norm_word = normalize_word(word)
            normalized_word_obj.append(BlackWord(word=norm_word))

        BlackWord.objects.bulk_create(normalized_word_obj, batch_size=50)

        return Response(
            data={'detail': f'After normalized, we will ban next words: {', '.join(list(map(str, normalized_word_obj)))}'},
            status=status.HTTP_200_OK
        )
