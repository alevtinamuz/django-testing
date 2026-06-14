from datetime import timedelta
import pytest

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='author')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='not author')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='news',
        text='text news',
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='text comment',
    )


@pytest.fixture
def news_id_for_args(news):
    return (news.id,)


@pytest.fixture
def comment_id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def form_data():
    return {'text': 'new text comment'}


@pytest.fixture
def many_news():
    today = timezone.now()
    News.objects.bulk_create(
        News(
            title=f'news_{idx}',
            text='text',
            date=today - timedelta(days=idx),
        )
        for idx in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def detail_url(news, news_id_for_args):
    return reverse('news:detail', args=news_id_for_args)


@pytest.fixture
def url_to_comments(detail_url):
    return detail_url + '#comments'
