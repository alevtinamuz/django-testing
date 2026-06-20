from http import HTTPStatus
import pytest
from pytest_lazyfixture import lazy_fixture as lf
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client, home_url):
    response = client.get(home_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_availability_detail_page_for_anonymous_user(
    client,
    detail_url,
):
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (lf('edit_url'), lf('delete_url')),
)
def test_redirect_edit_and_delete_pages_for_anonymous_user(
    client,
    url,
    login_url
):
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
    'url',
    (lf('edit_url'), lf('delete_url')),
)
def test_availability_edit_and_delete_pages_for_other_user(
    parametrized_client,
    url,
    expected_status
):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (lf('login_url'), lf('signup_url'), lf('logout_url')),
)
def test_availability_auth_pages_for_anonymous_user(client, url):
    if 'logout' in url:
        response = client.post(url)
    else:
        response = client.get(url)
    assert response.status_code == HTTPStatus.OK
