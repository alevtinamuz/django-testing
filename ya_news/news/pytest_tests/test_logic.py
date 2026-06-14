from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_note(
    author_client,
    detail_url,
    form_data,
    url_to_comments,
    news,
    author,
):
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, detail_url, form_data):
    response = client.post(detail_url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_comment_with_bad_words(
    author_client,
    detail_url,
):
    comment_with_bad_word = {'text': f'text with bad word {BAD_WORDS[0]}'}
    response = author_client.post(detail_url, data=comment_with_bad_word)
    assert 'form' in response.context
    form = response.context['form']
    assert form.errors['text'] == [WARNING]
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client,
    comment,
    url_to_comments,
    form_data,
):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data=form_data)
    assert response.url == url_to_comments
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_author_can_delete_comment(
    author_client,
    comment,
    url_to_comments,
):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_another_user_cant_edit_comment(
    not_author_client,
    comment,
    form_data,
):
    old_text = comment.text
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_text


def test_another_user_cant_delete_comment(
    not_author_client,
    comment,
):
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
