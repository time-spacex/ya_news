import pytest

from django.urls import reverse
from django.conf import settings


HOME_URL = 'news:home'


def get_response_object(client_type, url_namespace=HOME_URL, args=None):
    """Универсальная функция получения объекта response."""
    if url_namespace == HOME_URL:
        response = client_type.get(reverse(HOME_URL))
    else:
        response = client_type.get(reverse(url_namespace, args=args))
    return response


@pytest.mark.django_db
def test_news_count(client, fresh_news):
    """Тест количества новостей на главной странице."""
    object_list = get_response_object(client).context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, fresh_news):
    """Тест количества новостей на главной странице."""
    object_list = get_response_object(client).context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news_id, fresh_comments):
    """Тест сортировки комментариев на странице отдельной новости."""
    news = get_response_object(client, 'news:detail', news_id).context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_id):
    """Тест недоступности формы комментария для анонимного пользователя."""
    assert 'form' not in get_response_object(
        client,
        'news:detail',
        news_id
    ).context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, news_id):
    """Тест доступности формы комментария для авторизованного пользователя."""
    assert 'form' in get_response_object(
        author_client,
        'news:detail',
        news_id
    ).context
