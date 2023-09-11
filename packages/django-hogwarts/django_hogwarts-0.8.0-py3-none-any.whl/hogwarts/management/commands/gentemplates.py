from django.core.management.base import BaseCommand


from ...magic_templates.gen_templates import gen_templates

class Command(BaseCommand):
    help = "Code generation command"

    def add_arguments(self, parser):
        parser.add_argument("app", type=str)

    def handle(self, *args, **options):
        app_name: str = options["app"]
        gen_templates(app_name)
