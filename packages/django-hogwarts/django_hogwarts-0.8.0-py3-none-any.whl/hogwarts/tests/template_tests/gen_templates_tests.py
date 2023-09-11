import os

from django.apps import apps
from django import forms
from django.views.generic import FormView, RedirectView

from hogwarts.magic_templates.gen_templates import Endpoint, get_endpoint, ViewType
from hogwarts.magic_urls.gen_urls import get_app_name
from hogwarts.magic_urls.utils import extract_paths
from hogwarts.views import ExampleCreateView
from hogwarts.models import Article

base_path = apps.get_app_config("hogwarts").path
urls_code = open(os.path.join(base_path, "urls.py"), "r").read()

paths = extract_paths(urls_code)
app_name = get_app_name(urls_code)


def test_it_gets_endpoint():
    endpoint = get_endpoint(ExampleCreateView, paths, app_name)

    expected = Endpoint(
        view=ExampleCreateView,
        template_name=ExampleCreateView.template_name,
        path_name="example:create",
        view_type=ViewType.CREATE,
        model=ExampleCreateView.model
    )

    assert endpoint == expected


def test_it_tries_to_get_model_from_form_class():
    class ArticleForm(forms.ModelForm):
        class Meta:
            model = Article
            fields = ["title", "description"]

    class ArticleFormView(FormView):
        form_class = ArticleForm
        template_name = "form.html"
        success_url = "/"

    endpoint = get_endpoint(ArticleFormView, paths, app_name)

    assert endpoint.model == Article


def test_it_sets_null_if_no_model():
    class MyRedirectView(RedirectView):
        def get_redirect_url(self, *args, **kwargs):
            return "/"

    endpoint = get_endpoint(MyRedirectView, paths, app_name)

    assert endpoint.model is None
