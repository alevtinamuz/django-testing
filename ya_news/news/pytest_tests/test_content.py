from datetime import timedelta
import pytest
from pytest_lazyfixture import lazy_fixture as lf

from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from news.forms import CommentForm
from news.models import Comment

HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_news_count(client, many_news):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, many_news):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, author, news_id_for_args):
    today = timezone.now()
    for idx in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'text_{idx}',
        )
        comment.created = today + timedelta(days=idx)
        comment.save()
    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    assert 'news' in response.context
    news_obj = response.context['news']
    all_comments = news_obj.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
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
    news_id_for_args,
):
    url = reverse('news:detail', args=news_id_for_args)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_visible
    if form_visible:
        assert isinstance(response.context['form'], CommentForm)
