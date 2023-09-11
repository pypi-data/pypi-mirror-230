import inspect
import re
from dataclasses import dataclass
from enum import Enum
from inspect import isclass
from typing import Optional, Type

from django.views import View
from django.views.generic import DeleteView, DetailView, UpdateView

from hogwarts.utils import to_plural

detail_names = ["Detail", "Update", "Delete"]
BASE_CLASS_NAMES = [
    'View', 'ListView', 'CreateView', 'FormView', 'DetailView',
    'DeleteView', 'UpdateView', 'RedirectView', 'TemplateView',
    'ArchiveIndexView', 'DayArchiveView', 'MonthArchiveView',
    'YearArchiveView', 'TodayArchiveView', 'WeekArchiveView'
]


class ViewType(Enum):
    FUNCTION = 1
    CLASS = 2


@dataclass
class Path:
    path_name: str
    detail: bool
    path_urls: Optional[str]


def get_path_name(view, app_name: Optional[str] = None):
    name: str = view.__name__
    view_type = ViewType.CLASS if isclass(view) else ViewType.FUNCTION

    if app_name:
        if view_type == ViewType.CLASS:
            app_name = app_name.capitalize()

        if app_name in name:
            name = name.replace(app_name, '')

        elif app_name.endswith('s') and app_name[:-1] in name:
            name = name.replace(app_name[:-1], '')

    name = name.replace('View', '').replace('view', '')
    name = name.strip("_")

    return camel_to_snake(name)


def get_path_url(path_name: str, model_name: str = "none", detail=False):
    if not detail and path_name == "list":
        return ""

    model_name = model_name.lower()
    if path_name.startswith(model_name):
        path_url = path_name.replace(f"{model_name}_", "")
        path_url = path_url.replace("_", "-")

        if detail:
            path_url = path_url.replace("detail", "")
            if path_url == "":
                return f"{to_plural(model_name)}/<int:pk>/"
            return f"{to_plural(model_name)}/<int:pk>/{path_url}/"

        if path_url == "list":
            return f"{to_plural(model_name)}/"
        return f"{to_plural(model_name)}/{path_url}/"

    path_url = path_name.replace("_", "-") + "/"

    if path_name == 'detail':
        path_url = "<int:pk>/"

    elif detail:
        path_url = "<int:pk>/" + path_url

    return path_url


def view_is_detail(view_class: Type[View]):
    for cls in [DeleteView, DetailView, UpdateView]:
        if issubclass(view_class, cls):
            return True

    return any(ending in view_class.__name__ for ending in detail_names)


def camel_to_snake(camel_case_string):
    snake_case_string = re.sub(r'(?<=[a-z])([A-Z])', r'_\1', camel_case_string)
    snake_case_string = snake_case_string.lower()
    return snake_case_string


def import_views(views_module):
    members = inspect.getmembers(views_module, predicate=is_view)
    return [t[1] for t in members]


def is_view(obj):
    try:
        name = obj.__name__
    except AttributeError:
        return False

    ends_with_view = name.lower().endswith("view")
    not_base_class = name not in BASE_CLASS_NAMES

    return ends_with_view and not_base_class
