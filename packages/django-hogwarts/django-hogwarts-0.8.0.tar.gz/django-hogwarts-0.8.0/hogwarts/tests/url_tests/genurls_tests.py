import os

from pytest import fixture
from django.apps import apps

from hogwarts.magic_urls.base import import_views
from hogwarts.magic_urls.gen_urls import gen_path, UrlGenerator
from hogwarts.magic_urls import custom_path

from hogwarts import _test_views
from hogwarts.utils import code_strip


def test_it_generates_path():
    result = gen_path(_test_views.MyListView, "my")
    expected = 'path("", MyListView.as_view(), name="list")'

    assert result == expected


def test_it_generates_path_for_function():
    result = gen_path(_test_views.confirm_post_view, "none")
    expected = 'path("confirm-post/", confirm_post_view, name="confirm_post")'

    assert result == expected


def test_it_extracts_metadata():
    @custom_path("green", "green-hello/")
    class RedView:
        pass

    result = gen_path(RedView, "none")
    expected = 'path("green-hello/", RedView.as_view(), name="green")'

    assert result == expected


views = import_views(_test_views)


@fixture
def generator():
    base_url = apps.get_app_config("hogwarts").path
    return UrlGenerator(_test_views, os.path.join(base_url, "urls.py"), "my", True)


def test_it_generates_urls(generator):
    result = generator.gen_urlpatterns(views)

    expected = """
    urlpatterns = [
        path("form/", MyFormView.as_view(), name="form"),
        path("", MyListView.as_view(), name="list"),
        path("confirm-post/", confirm_post_view, name="confirm_post"),
        path("get/", get_view, name="get"),
        path("post/", post_view, name="post")
    ]"""

    assert result == code_strip(expected)


def test_it_generates_imports(generator):
    result = generator.gen_url_imports([
        _test_views.MyListView,
        _test_views.MyFormView,
        _test_views.get_view
    ])

    expected = """
        from django.urls import path
    
        from .views import MyListView, MyFormView, get_view
    """

    assert code_strip(result) == code_strip(expected)
