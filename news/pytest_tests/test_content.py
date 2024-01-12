import pytest

from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm


HOME_URL = 'news:home'


@pytest.mark.django_db
def test_news_count(client, fresh_news):
    """Тест количества новостей на главной странице."""
    object_list = client.get(reverse(HOME_URL)).context.get('object_list')
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, fresh_news):
    """Тест сортировки новостей на главной странице."""
    object_list = client.get(reverse(HOME_URL)).context.get('object_list')
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news_id, fresh_comments):
    """Тест сортировки комментариев на странице отдельной новости."""
    news = client.get(reverse('news:detail', args=news_id)).context.get('news')
    all_comments_dates = [comment.created for comment in news.comment_set.all()]
    all_comments_dates_sorted = sorted(all_comments_dates)
    assert all_comments_dates == all_comments_dates_sorted


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_id):
    """Тест недоступности формы комментария для анонимного пользователя."""
    assert 'form' not in client.get(reverse('news:detail', args=news_id)).context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, news_id):
    """Тест доступности формы комментария для авторизованного пользователя."""
    response = author_client.get(reverse('news:detail', args=news_id))
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm) == True
