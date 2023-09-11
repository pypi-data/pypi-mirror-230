import os
import re
from inspect import isclass
from typing import Tuple, Optional

from hogwarts.magic_urls.base import import_views, get_path_name, get_path_url, view_is_detail
from .decorators import PathDecorator


class BaseUrl:
    def __init__(self, views_module, urls_path: str, app_name, force_app_name=False, single_import=False):
        self.views_module = views_module
        self.urls_path = urls_path
        self.app_name = None
        self.single_import = single_import

        if force_app_name:
            self.app_name = app_name
        else:
            self.app_name = read_app_name(self.urls_path) or app_name

    def write(self, imports, urlpatterns):
        code = f'{imports}\n\napp_name = "{self.app_name}"\n{urlpatterns}\n'

        with open(f"{self.urls_path}", 'w') as file:
            file.write(code)


class UrlGenerator(BaseUrl):
    def gen_urls_py(self):
        """
        generates code for urls.py
        fully overrides any existing code
        """
        views = import_views(self.views_module)

        imports = self.gen_url_imports(views)
        urlpatterns = self.gen_urlpatterns(views)

        self.write(imports, urlpatterns)

    def gen_url_imports(self, views: list[object]):
        if self.single_import:
            return "from django.urls import path\n\nfrom . import views"
        view_names = ", ".join(view.__name__ for view in views)
        return f"from django.urls import path\n\nfrom .views import {view_names}\n"

    def gen_urlpatterns(self, views):
        paths = []

        for view in views:
            paths.append(gen_path(view, self.app_name, self.single_import))

        paths_string = ",\n    ".join(paths)
        result = f'urlpatterns = [\n    {paths_string.strip()}\n]'

        return result


class UrlMerger(BaseUrl):
    def merge_urls_py(self):
        """
        adds new paths without touching existing paths
        """
        file = open(self.urls_path, "r")
        code = file.read()

        imports, urlpatterns = separate_imports_and_urlpatterns(code)
        views = import_views(self.views_module)

        imports = self.merge_url_imports(imports, urlpatterns, views)
        urlpatterns = self.merge_urlpatterns(urlpatterns, views)

        self.write(imports, urlpatterns)

    def merge_url_imports(self, imports, urlpatterns, views):
        if not self.single_import:
            for view in views:
                if view.__name__ not in urlpatterns:
                    imports = append_view_into_imports(imports, view.__name__)

        return imports

    def merge_urlpatterns(self, urlpatterns, views):
        paths: list[Tuple[str, str]] = []

        for view in views:
            path = gen_path(view, self.app_name, self.single_import)
            paths.append((path, view.__name__))

        for path in paths:
            if path[1] not in urlpatterns:
                urlpatterns = append_path_into_urlpatterns(urlpatterns, path[0])

        return urlpatterns


def gen_path(view, app_name, from_view_file=False) -> str:
    decorator = PathDecorator(view)
    if decorator.exists():
        path_name = decorator.get_path_name()
        path_url = decorator.get_path_url()

        print(
            f"info: You have provided @custom_path decorator in {view.__name__}"
            f"don't forget to remove because it is not in use anymore"
        )
    else:
        path_name = get_path_name(view, app_name)
        model = getattr(view, "model", False)
        path_url = get_path_url(
            path_name,
            model_name=model.__name__ if model else "none",
            detail=view_is_detail(view) if isclass(view) else False
        )

    view_name = view.__name__
    view_function = f"{view_name}.as_view()" if isclass(view) else view_name
    view_function = f"views.{view_function}" if from_view_file else view_function

    return f'path("{path_url}", {view_function}, name="{path_name}")'


# Warning. below are purely algorithmic functions, no need to read


def separate_imports_and_urlpatterns(code: str) -> Tuple[str, str]:
    imports = ""
    urlpatterns = ""

    lines = code.splitlines()

    for i in range(len(lines)):
        if lines[i].startswith("from"):
            imports += lines[i] + "\n"

            if lines[i].endswith("("):
                x = i + 1
                while not lines[x].endswith(")"):
                    imports += lines[x] + "\n"
                    x += 1
                imports += lines[x] + "\n"

        if lines[i].startswith("urlpatterns"):
            for x in range(i, len(lines)):
                urlpatterns += lines[x] + "\n"
            break

    return imports, urlpatterns


def append_view_into_imports(imports: str, view: str):
    lines = imports.splitlines()

    if "from .views" not in imports:
        lines.append("from .views import")

    for i in range(len(lines)):
        if lines[i].startswith("from .views"):
            if lines[i].endswith("("):
                x = i + 1
                while not lines[x].endswith(")"):
                    x += 1

                if lines[x].strip() == ")":
                    lines[x - 1] += ","
                    lines[x] = lines[x].replace(")", f"    {view}\n)")
                else:
                    lines[x] = lines[x].replace(")", f", {view})")

                break

            if lines[i].strip().endswith("import"):
                lines[i] = lines[i].strip()
                lines[i] += " " + view
            else:
                tokens = lines[i].split(" ")
                if view not in tokens:
                    lines[i] += ", " + view

            break

    return "\n".join(lines)


def append_path_into_urlpatterns(urlpatterns: str, path: str):
    lines = urlpatterns.splitlines()
    lines = [line.rstrip() for line in lines]
    bracket = None

    for i, line in enumerate(lines):
        if "]" in line:
            bracket = i
            break

    if bracket:
        if not lines[bracket - 1].endswith(","):
            lines[bracket - 1] = lines[bracket - 1] + ","

        lines[bracket] = "    " + path
        lines.append("]")

    return "\n".join(lines)


def get_app_name(code: str) -> Optional[str]:
    lines = code.splitlines()

    for line in lines:
        if line.startswith("app_name"):
            pattern = r'"([^"]*)"'
            match = re.search(pattern, line)
            return match.group(1)

    return None


def urlpatterns_is_empty(code):
    if code.strip() == "" or "urlpatterns" not in code:
        return True

    result = re.search(r'urlpatterns\s*=\s*\[\s*\]', code)
    return result is not None


def read_app_name(urls_path: str):
    if not os.path.exists(urls_path):
        return None

    file = open(urls_path, "r")
    code = file.read()

    return get_app_name(code)
