from hogwarts.magic_views.gen_imports import ImportsGenerator
from hogwarts.utils import code_strip

code = """
import ast
import datetime

from django.views.generic import DetailView, ListView
from .forms import MyForm
"""


def test_it_generates_imports_from_code():
    gen = ImportsGenerator()
    expected = {
        None: ["ast", "datetime"],
        "django.views.generic": ["DetailView", "ListView"],
        ".forms": ["MyForm"],
    }
    gen.parse_imports(code_strip(code))

    assert gen.get_merge_imports() == expected


def test_it_merges_import_with_code():
    gen = ImportsGenerator()

    expected_code = """
    import ast, datetime
    from django.views.generic import DetailView, ListView, UpdateView
    from .forms import MyForm, YouForm
    """

    gen.parse_imports(code_strip(code))
    gen.add("django.views.generic", "UpdateView")
    gen.add(".forms", "YouForm")

    assert gen.gen() == code_strip(expected_code)
