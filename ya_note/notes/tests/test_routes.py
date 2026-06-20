from http import HTTPStatus

from .test_base import (
    BaseTestCase,
    HOME_URL, LIST_URL, ADD_URL, SUCCESS_URL,
    LOGIN_URL, LOGOUT_URL, SIGNUP_URL
)


class TestRoutes(BaseTestCase):

    def test_availability_home_page(self):
        response = self.client.get(HOME_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_pages_for_auth_user(self):
        urls = (LIST_URL, ADD_URL, SUCCESS_URL)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_note_pages_only_for_author(self):
        users = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        urls = (self.detail_url, self.edit_url, self.delete_url)
        for user, status in users:
            for url in urls:
                with self.subTest(user=user, url=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            LIST_URL, SUCCESS_URL, ADD_URL,
            self.detail_url, self.edit_url, self.delete_url
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_auth_pages_for_all_users(self):
        users = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.OK),
            (self.client, HTTPStatus.OK),
        )
        urls = (LOGIN_URL, LOGOUT_URL, SIGNUP_URL)
        for user, status in users:
            for url in urls:
                with self.subTest(user=user, url=url):
                    if 'logout' in url:
                        response = user.post(url)
                    else:
                        response = user.get(url)
                    self.assertEqual(response.status_code, status)
