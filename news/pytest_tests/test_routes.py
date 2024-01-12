from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_pages_availability(client, name, args):
    """
    Тест доступности домашней страницы, детализации, логина,
    логаута и регистрации для пользователей.
    """
    assert client.get(reverse(name, args=args)).status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, name, comment_id, expected_status
):
    """Тест доступности страниц редактирования и удаления комментария."""
    assert parametrized_client.get(
        reverse(name, args=comment_id)
    ).status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_for_anonymous_client(client, name, comment_id):
    """Тест страниц перенаправления для анонимного клиента."""
    login_url = reverse('users:login')
    url = reverse(name, args=comment_id)
    response = client.get(url)
    redirect_url = f'{login_url}?next={url}'
    assertRedirects(response, redirect_url)
