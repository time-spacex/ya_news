import pytest

from http import HTTPStatus

from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


FORM_DATA = {'text': 'Текст комментария'}
NEW_FORM_DATA = {'text': 'Новый текст комментария'}


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news_id):
    """Тест невозможности комментирования анонимному пользователю."""
    url = reverse('news:detail', args=news_id)
    client.post(url, datd=FORM_DATA)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(author, author_client, news, news_id):
    """Тест возможности комментирования авторизованному пользователю."""
    url = reverse('news:detail', args=news_id)
    response = author_client.post(url, data=FORM_DATA)
    redirect_url = f'{url}#comments'
    comments_count = Comment.objects.count()
    comment = Comment.objects.get()
    assert response.url == redirect_url
    assert comments_count == 1
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news_id):
    """Тест невозможности использования плохих слов в форме комментария."""
    url = reverse('news:detail', args=news_id)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    comments_count = Comment.objects.count()
    assert response.context['form'].errors['text'][0] == WARNING
    assert comments_count == 0


def test_author_can_delete_comment(author_client, news_id, comment_id):
    """Тест возможности автором удаления своего комментария."""
    url = reverse('news:detail', args=news_id)
    delete_url = reverse('news:delete', args=comment_id)
    response = author_client.delete(delete_url)
    redirect_url = f'{url}#comments'
    comments_count = Comment.objects.count()
    assert response.url == redirect_url
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(reader_client, comment_id):
    """Тест невозможности пользователя удаления несвоего комментария."""
    delete_url = reverse('news:delete', args=comment_id)
    response = reader_client.delete(delete_url)
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count == 1


def test_author_can_edit_comment(author_client, news_id, comment, comment_id):
    """Тест возможности автором редактирования своего комментария."""
    url = reverse('news:detail', args=news_id)
    edit_url = reverse('news:edit', args=comment_id)
    response = author_client.post(edit_url, data=NEW_FORM_DATA)
    redirect_url = f'{url}#comments'
    comment.refresh_from_db()
    assert response.url == redirect_url
    assert comment.text == NEW_FORM_DATA['text']


def test_user_cant_edit_comment_of_another_user(
    reader_client,
    comment_id,
    comment
):
    """Тест невозможности пользователем редактирования несвоего комментария."""
    edit_url = reverse('news:edit', args=comment_id)
    response = reader_client.post(edit_url, data=FORM_DATA)
    comment.refresh_from_db()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == FORM_DATA['text']
