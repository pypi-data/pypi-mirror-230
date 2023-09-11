from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from .base import get_app_config


class Command(BaseCommand):
    help = "scaffold model (generate views, urls and templates at once)"

    def add_arguments(self, parser):
        parser.add_argument("app_name", type=str)

    def handle(self, *args, **options):
        app_name = options["app_name"]

        app_config = get_app_config(app_name)

        for model in app_config.get_models():
            try:
                call_command("genviews", app_name, model.__name__, "-s", "-mn")
            except CommandError as e:
                self.stderr.write(self.style.ERROR(f"Could not generate views for model {model.__name__}: {e}"))

        try:
            call_command("genurls", app_name, "-s")
        except CommandError as e:
            self.stderr.write(self.style.ERROR(f"Could not generate urls: {e}"))

        try:
            call_command("gentemplates", app_name)
        except CommandError as e:
            self.stderr.write(self.style.ERROR(f"Could not generate templates: {e}"))
