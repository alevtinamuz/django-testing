from http import HTTPStatus
import pytest
from pytest_lazyfixture import lazy_fixture as lf
from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_availability_detail_page_for_anonymous_user(
    client,
    news_id_for_args,
):
    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_edit_and_delete_pages_for_anonymous_user(
    client,
    name,
    comment_id_for_args,
):
    login_url = reverse('users:login')
    url = reverse(name, args=comment_id_for_args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('author_client'), HTTPStatus.OK),
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_availability_edit_and_delete_pages_for_other_user(
    parametrized_client,
    name,
    comment_id_for_args,
    expected_status
):
    url = reverse(name, args=comment_id_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('users:login', 'users:signup', 'users:logout'),
)
def test_availability_auth_pages_for_anonymous_user(client, name):
    url = reverse(name)
    if 'logout' in url:
        response = client.post(url)
    else:
        response = client.get(url)
    assert response.status_code == HTTPStatus.OK
