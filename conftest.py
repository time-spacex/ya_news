from datetime import datetime, timedelta
import random

from django.conf import settings
from django.utils import timezone
import pytest

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def fresh_news():
    News.objects.bulk_create(
        [
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=datetime.today() - timedelta(days=random.randint(1, 11))
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
    )


@pytest.fixture
def fresh_comments(news, author):
    for index in range(2):
        fresh_comments = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст комментария {index}',
        )
        fresh_comments.created = timezone.now() - timedelta(days=index)
        fresh_comments.save()


@pytest.fixture
def news_id(news):
    return (news.id,)


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def comment_id(comment):
    return (comment.id,)
