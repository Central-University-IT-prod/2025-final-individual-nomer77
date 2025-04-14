from django.test import TestCase
from unittest.mock import patch, MagicMock
from moderation.models import BlackWord
from moderation.utils import normalize_word, get_bad_words, check_bad_words


class NormalizeWordTests(TestCase):
    def test_normalize_word(self):
        word = "Кошки"
        normalized = normalize_word(word)
        self.assertEqual(normalized, "кошка")

    def test_normalize_word_no_change(self):
        word = "кот"
        normalized = normalize_word(word)
        self.assertEqual(normalized, "кот")


class GetBadWordsTests(TestCase):
    def setUp(self):
        BlackWord.objects.create(word="плохой")
        BlackWord.objects.create(word="ужасный")

    def test_get_bad_words(self):
        bad_words = get_bad_words()
        self.assertIsInstance(bad_words, set)
        self.assertIn("плохой", bad_words)
        self.assertIn("ужасный", bad_words)


class CheckBadWordsTests(TestCase):
    def setUp(self):
        BlackWord.objects.create(word="плохой")

    def test_check_bad_words_found(self):
        text = "Это очень плохой день."
        result = check_bad_words(text)
        self.assertTrue(result)

    def test_check_bad_words_plural_found(self):
        text = "Это очень плохие дни."
        result = check_bad_words(text)
        self.assertTrue(result)

    def test_check_bad_words_not_found(self):
        text = "Это хороший день."
        result = check_bad_words(text)
        self.assertFalse(result)

    def test_check_bad_words_with_custom_list(self):
        text = "Это ужасный день."
        result = check_bad_words(text, bad_words=["ужасный"])
        self.assertTrue(result)

    def test_check_bad_words_empty_list(self):
        text = "Это ужасный день."
        result = check_bad_words(text, bad_words=[])
        self.assertFalse(result)

    @patch('moderation.utils.normalize_word')
    def test_check_bad_words_normalized(self, mock_normalize):
        mock_normalize.side_effect = lambda word: word
        text = "Плохой"
        result = check_bad_words(text)
        self.assertTrue(result)
        mock_normalize.assert_called()
