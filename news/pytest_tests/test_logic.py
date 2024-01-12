from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


FORM_DATA = {'text': 'Текст комментария'}
NEW_FORM_DATA = {'text': 'Новый текст комментария'}


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news_id):
    """Тест невозможности комментирования анонимному пользователю."""
    url = reverse('news:detail', args=news_id)
    client.post(url, data=FORM_DATA)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author, author_client, news, news_id):
    """Тест возможности комментирования авторизованному пользователю."""
    url = reverse('news:detail', args=news_id)
    response = author_client.post(url, data=FORM_DATA)
    redirect_url = f'{url}#comments'
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 1
    assert Comment.objects.get().text == FORM_DATA['text']
    assert Comment.objects.get().news == news
    assert Comment.objects.get().author == author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, news_id, bad_word):
    """Тест невозможности использования плохих слов в форме комментария."""
    bad_words_data = {'text': f'Какой-то текст, {bad_word}, еще текст'}
    response = author_client.post(
        reverse('news:detail', args=news_id),
        data=bad_words_data
    )
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, news_id, comment_id):
    """Тест возможности автором удаления своего комментария."""
    url = reverse('news:detail', args=news_id)
    response = author_client.delete(reverse('news:delete', args=comment_id))
    redirect_url = f'{url}#comments'
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(reader_client, comment_id):
    """Тест невозможности пользователя удаления несвоего комментария."""
    response = reader_client.delete(reverse('news:delete', args=comment_id))
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, news_id, comment, comment_id):
    """Тест возможности автором редактирования своего комментария."""
    url = reverse('news:detail', args=news_id)
    response = author_client.post(
        reverse('news:edit', args=comment_id),
        data=NEW_FORM_DATA
    )
    redirect_url = f'{url}#comments'
    comment.refresh_from_db()
    assertRedirects(response, redirect_url)
    assert comment.text == NEW_FORM_DATA['text']


def test_user_cant_edit_comment_of_another_user(
    reader_client,
    comment_id,
    comment
):
    """Тест невозможности пользователем редактирования несвоего комментария."""
    comment_text = comment.text
    response = reader_client.post(
        reverse('news:edit', args=comment_id),
        data=FORM_DATA
    )
    comment.refresh_from_db()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == comment_text
