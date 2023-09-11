from typing import Optional

from hogwarts.magic_urls.base import Path, get_path_url


def custom_path(
        path_name: str,
        path_url: Optional[str] = None,
        detail: bool = False
):
    def wrapper(obj):
        obj.auto_url_path = Path(path_name, detail, path_url)
        return obj

    return wrapper


class PathDecorator:
    def __init__(self, view):
        self.view = view

    def exists(self):
        return hasattr(self.view, "auto_url_path")

    def get_path_name(self):
        path: Path = getattr(self.view, "auto_url_path")
        return path.path_name

    def get_path_url(self):
        path: Path = getattr(self.view, "auto_url_path")
        path_name = self.get_path_name()
        return path.path_urls or get_path_url(path_name, detail=path.detail)
