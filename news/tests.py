from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError
from news.models import News, NewsCategory, DailyEvent
from news.forms import NewsForm


class DailyNewsGroupingTestCase(TestCase):
    def setUp(self):
        self.category = NewsCategory.objects.create(
            name="Акции",
            slug="promotions",
            description="Категория акций"
        )
        self.test_date = date(2026, 7, 29)

    def test_create_single_news(self):
        """Тест создания первой новости на указанную дату"""
        news1 = News.objects.create(
            title="Первая новость",
            slug="first-news",
            category=self.category,
            news_date=self.test_date,
            content="<p>Текст первой новости</p>"
        )
        self.assertEqual(News.objects.count(), 1)
        self.assertEqual(news1.title, "Первая новость")

    def test_publish_news_same_date_appends_event(self):
        """Тест добавления второй новости в ту же дату: не должно вызывать ошибку, а добавлять событие"""
        news1 = News.objects.create(
            title="Первая новость",
            slug="first-news",
            category=self.category,
            news_date=self.test_date,
            content="<p>Текст первой новости</p>"
        )
        
        # Создаем вторую новость на ту же дату и категорию
        news2 = News(
            title="Вторая новость",
            slug="second-news",
            category=self.category,
            news_date=self.test_date,
            content="<p>Текст второй новости</p>"
        )
        
        # Валидация уникальности должна пройти успешно
        try:
            news2.full_clean()
        except ValidationError as e:
            self.fail(f"full_clean() вызвал ValidationError при попытке добавить новость на ту же дату: {e}")
            
        news2.save()
        
        # Запись в БД по-прежнему 1
        self.assertEqual(News.objects.filter(category=self.category, news_date=self.test_date).count(), 1)
        
        # У этой новости должно быть 2 события
        updated_news = News.objects.get(pk=news1.pk)
        self.assertEqual(updated_news.events.count(), 2)
        
        event_titles = list(updated_news.events.values_list('title', flat=True))
        self.assertIn("Первая новость", event_titles)
        self.assertIn("Вторая новость", event_titles)
        
        # Контент обновился и включает оба события
        self.assertIn("Первая новость", updated_news.content)
        self.assertIn("Вторая новость", updated_news.content)

    def test_news_form_validation_same_date(self):
        """Тест работы формы NewsForm при публикации новости на ту же дату"""
        News.objects.create(
            title="Первая новость",
            slug="first-news",
            category=self.category,
            news_date=self.test_date,
            content="<p>Текст первой новости</p>"
        )
        
        form_data = {
            'title': 'Формовая вторая новость',
            'slug': 'form-second-news',
            'category': self.category.id,
            'news_date': self.test_date.strftime('%Y-%m-%d'),
            'content': '<p>Контент формовой новости</p>',
            'views': 0,
            'is_active': True,
        }
        
        form = NewsForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Форма невалидна: {form.errors}")
        
        saved_news = form.save()
        self.assertEqual(News.objects.count(), 1)
        self.assertIn("Формовая вторая новость", saved_news.content)
