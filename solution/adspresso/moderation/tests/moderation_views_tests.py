from rest_framework import status
from rest_framework.test import APITestCase
from moderation.models import ModerationSettings, BlackWord
from moderation.utils import normalize_word


class ModerationOnAPIViewTest(APITestCase):
    def setUp(self):
        self.url = '/moderation/status/on'
        ModerationSettings.objects.create(moderate=False)

    def test_enable_moderation(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Moderation was enabled.')
        obj = ModerationSettings.get_moderation_settings_object()
        self.assertTrue(obj.moderate)


class ModerationOffAPIViewTest(APITestCase):
    def setUp(self):
        self.url = '/moderation/status/off'
        ModerationSettings.objects.create(moderate=True)

    def test_disable_moderation(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Moderation was disabled.')
        obj = ModerationSettings.get_moderation_settings_object()
        self.assertFalse(obj.moderate)


class AddNewWordsAPIViewTest(APITestCase):
    def setUp(self):
        self.url = '/moderation/words'

    def test_add_words_success(self):
        words = ['badword', 'offensive']
        normalized_words = [normalize_word(w) for w in words]
        response = self.client.post(self.url, data={'words': words}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(BlackWord.objects.filter(word__in=normalized_words).exists())
        for word in normalized_words:
            self.assertTrue(BlackWord.objects.filter(word=word).exists())

    def test_add_words_no_words_field(self):
        response = self.client.post(self.url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'words is required field.')

    def test_add_words_not_list(self):
        response = self.client.post(self.url, data={'words': 'notalist'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'words must be a list of ban words.')
