from django.test import TestCase
from django.core.cache import cache
from timeline.models import TimeLine

class TimeLineTests(TestCase):
    def setUp(self):
        cache.clear()  # Очищаем кэш перед каждым тестом

    def test_get_current_date_object_from_db(self):
        """ Проверяет, что объект создается в БД, если его нет в кэше """
        obj = TimeLine.get_current_date_object()
        self.assertEqual(obj.current_date, 0)
        self.assertEqual(TimeLine.objects.count(), 1)

    def test_get_current_date_object_from_cache(self):
        """ Проверяет, что объект извлекается из кэша, если он там есть """
        # Создаем объект и сохраняем его в кэш
        TimeLine.objects.create(current_date=5)
        cache.set("timeline:current_date", 5)

        obj = TimeLine.get_current_date_object()
        self.assertEqual(obj.current_date, 5)
        self.assertEqual(TimeLine.objects.count(), 1)  # В БД уже есть объект, новый не создавался

    def test_save_updates_cache(self):
        """ Проверяет, что при сохранении объект обновляет кэш """
        obj = TimeLine.objects.create(current_date=10)
        obj.current_date = 20
        obj.save()

        self.assertEqual(cache.get("timeline:current_date"), 20)

    def test_cache_miss_fetches_from_db(self):
        """ Проверяет, что если в кэше нет данных, они берутся из БД """
        TimeLine.objects.create(current_date=30)

        cache.delete("timeline:current_date")  # Удаляем данные из кэша
        obj = TimeLine.get_current_date_object()

        self.assertEqual(obj.current_date, 30)  # Должен взять из БД и закэшировать
        self.assertEqual(cache.get("timeline:current_date"), 30)