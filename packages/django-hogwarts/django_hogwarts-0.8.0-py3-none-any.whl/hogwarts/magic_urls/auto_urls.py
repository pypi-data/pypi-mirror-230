from inspect import isclass
from typing import Optional

from django.urls import path

from .base import (
    import_views,
    get_path_name,
    get_path_url,
    view_is_detail
)
from .decorators import PathDecorator


def auto_urls(views_module, app_name: str):
    views = import_views(views_module)
    urlpatterns = []

    for view in views:
        urlpatterns.append(get_path(view, app_name))

    return urlpatterns


def get_path(view, app_name: Optional[str] = None):
    decorator = PathDecorator(view)
    if decorator.exists():
        path_name = decorator.get_path_name()
        path_url = decorator.get_path_url()

    else:
        path_name = get_path_name(view, app_name)
        path_url = get_path_url(path_name, detail=view_is_detail(view))

    if isclass(view):
        return path(path_url, view.as_view(), name=path_name)
    else:
        return path(path_url, view, name=path_name)
