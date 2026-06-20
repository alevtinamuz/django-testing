import pytest
from pytest_lazyfixture import lazy_fixture as lf

from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, many_news, home_url):
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, many_news, home_url):
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, detail_url, comments_for_news):
    response = client.get(detail_url)
    assert 'news' in response.context
    news_obj = response.context['news']
    all_comments = news_obj.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'parametrized_client, form_visible',
    (
        (lf('client'), False),
        (lf('author_client'), True)
    )
)
def test_comment_form_visible(
    parametrized_client,
    form_visible,
    detail_url,
):
    response = parametrized_client.get(detail_url)
    assert ('form' in response.context) is form_visible
    if form_visible:
        assert isinstance(response.context['form'], CommentForm)
