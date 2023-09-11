import os

from django.core.management.base import BaseCommand
from rich.console import Console

from hogwarts.magic_urls.gen_urls import UrlGenerator, urlpatterns_is_empty, UrlMerger
from .base import get_app_config, get_views_module


console = Console()


class Command(BaseCommand):
    help = "urlpatterns generation from views.py"

    def add_arguments(self, parser):
        parser.add_argument("app_name", type=str)

        parser.add_argument(
            "--force-app-name", "-fan",
            action="store_true",
            help="use given app name rather than app_name in urls.py"
        )

        parser.add_argument(
            "--override", "-o",
            action="store_true",
            help="fully overrides urls.py"
        )

        parser.add_argument(
            "--single-import", "-s",
            action="store_true",
            help='import view like "from . import view" instead of importing individual view'
        )

    def handle(self, *args, **options):
        app_name: str = options["app_name"]
        force_new_app_name: bool = options["force_app_name"]
        override: bool = options["override"]
        single_import: bool = options["single_import"]

        views_module = get_views_module(app_name)
        app_config = get_app_config(app_name)
        urls_path = os.path.join(app_config.path, "urls.py")

        url_generator = UrlGenerator(views_module, urls_path, app_name, force_new_app_name, single_import)
        url_merger = UrlMerger(views_module, urls_path, app_name, force_new_app_name, single_import)

        code = ""
        if os.path.exists(urls_path):
            code = open(urls_path, "r").read()

        if not urlpatterns_is_empty(code) and not override:

            url_merger.merge_urls_py()
            console.print("existing paths detected 📜", style="bright_black")
            console.print("adding new paths...", style="bright_black")
            console.print("new paths merged to urlpatterns ✅", style="green")

        else:
            url_generator.gen_urls_py()
            console.print("adding new paths...", style="bright_black")
            console.print("urlpatterns have been generated ✅", style="green")

