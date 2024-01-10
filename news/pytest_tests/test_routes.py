import pytest

from django.urls import reverse

from http import HTTPStatus


def get_response_object(client_type, url_namespace, args):
    """Универсальная функция получения объекта response."""
    url = reverse(url_namespace, args=args)
    response = client_type.get(url)
    return response


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
    assert get_response_object(client, name, args).status_code == HTTPStatus.OK


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
    assert get_response_object(
        parametrized_client,
        name,
        comment_id
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
    assert response.url == redirect_url
