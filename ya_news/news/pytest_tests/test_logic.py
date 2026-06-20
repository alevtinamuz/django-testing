from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {'text': 'new text comment'}


def test_user_can_create_note(
    author_client,
    detail_url,
    url_to_comments,
    news,
    author,
):
    response = author_client.post(detail_url, data=FORM_DATA)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    created_comment = Comment.objects.get()
    assert created_comment.text == FORM_DATA['text']
    assert created_comment.author == author
    assert created_comment.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(
    client,
    detail_url,
    login_url,
):
    response = client.post(detail_url, data=FORM_DATA)
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
    edit_url,
):
    response = author_client.post(edit_url, data=FORM_DATA)
    assertRedirects(response, url_to_comments)
    edited_comment = Comment.objects.get(id=comment.id)
    assert edited_comment.text == FORM_DATA['text']
    assert edited_comment.author == comment.author
    assert edited_comment.news == comment.news
    assert Comment.objects.count() == 1


def test_author_can_delete_comment(
    author_client,
    comment,
    url_to_comments,
    delete_url,
):
    response = author_client.post(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_another_user_cant_edit_comment(
    not_author_client,
    comment,
    edit_url,
):
    response = not_author_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    edited_comment = Comment.objects.get(id=comment.id)
    assert edited_comment.text == comment.text
    assert edited_comment.author == comment.author
    assert edited_comment.news == comment.news
    assert Comment.objects.count() == 1


def test_another_user_cant_delete_comment(
    not_author_client,
    comment,
    delete_url,
):
    response = not_author_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    deleted_comment = Comment.objects.get(id=comment.id)
    assert deleted_comment.text == comment.text
    assert deleted_comment.news == comment.news
    assert deleted_comment.author == comment.author
