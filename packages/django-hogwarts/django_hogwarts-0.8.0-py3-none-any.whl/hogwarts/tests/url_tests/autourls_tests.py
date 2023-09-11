from django.urls import path
from django.views import View

from hogwarts import _test_views
from hogwarts._test_views import MyFormView, MyListView, get_view, post_view, confirm_post_view
from hogwarts.magic_urls.auto_urls import (
    get_path,
    get_path_name,
    import_views,
)
from hogwarts.magic_urls import custom_path
from hogwarts.magic_urls.base import get_path_url


class ProductCreateView(View): pass
class ProductsListView(View): pass
class ProductDetailView(View): pass
class SendMessageView(View): pass
class ConfirmOrderView(View): pass
def product_update_view(): pass
def dumb_files_view(): pass


def test_it_imports_user_defined_views():
    imported_classes = import_views(_test_views)
    expected = [MyFormView, MyListView, confirm_post_view, get_view, post_view]

    assert imported_classes == expected


def test_crud_get_path_name():
    payload = [
        (ProductCreateView, 'create'),
        (ProductsListView, 'list'),
        (ProductDetailView, 'detail'),
        (product_update_view, 'update')
    ]

    for view, expected_path_name in payload:
        path_name = get_path_name(view, 'products')
        assert path_name == expected_path_name


def test_detail_path_url():
    path_name = get_path_name(ProductDetailView, 'products')
    path_url = get_path_url(path_name, 'products')

    assert path_url == "<int:pk>/"


def test_get_path_name():
    payload = [
        (SendMessageView, "send_message"),
        (ConfirmOrderView, "confirm_order"),
        (dumb_files_view, "dumb_files")
    ]

    for view, expected_path_name in payload:
        path_name = get_path_name(view)
        assert path_name == expected_path_name


def test_auto_path_decorator():
    @custom_path("confirm", detail=True)
    class Some(View):
        pass

    expected_path = path("<int:pk>/confirm/", Some.as_view(), name="confirm")
    current_path = get_path(Some)

    assertPathEqual(expected_path, current_path)


def test_decorator_custom_url():
    path_url = "<int:pk>/products"

    @custom_path("confirm", path_url=path_url, detail=True)
    class Another(View):
        pass

    expected_path = path(path_url, Another.as_view(), name="confirm")
    current_path = get_path(Another)

    assertPathEqual(expected_path, current_path)


def assertPathEqual(path1, path2):
    assert path1.name == path2.name
    assert path1.pattern.regex == path2.pattern.regex
