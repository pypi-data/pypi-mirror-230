# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hogwarts',
 'hogwarts.magic_templates',
 'hogwarts.magic_urls',
 'hogwarts.magic_views',
 'hogwarts.management',
 'hogwarts.management.commands',
 'hogwarts.migrations',
 'hogwarts.tests',
 'hogwarts.tests.template_tests',
 'hogwarts.tests.url_tests',
 'hogwarts.tests.view_tests']

package_data = \
{'': ['*'], 'hogwarts': ['scaffold/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0', 'rich>=13.5.2,<14.0.0']

setup_kwargs = {
    'name': 'django-hogwarts',
    'version': '0.8.0',
    'description': 'Django utilities for codegen and DX improvement',
    'long_description': '<h1 align="center">Django hogwarts 🧙\u200d♂️</h1>\n<h4 align="center">Management commands to generate views, urls and templates</h4>\n\nUse CLI commands to generate:\n- basic create, update, list, detail views\n- urlpatterns from views with REST like path urls\n- form, table, detail templates (Bootstrap and django-crispy-forms by default)\n\n**all commands will respect (will not change) existing code**\n\n---\n\n## Installation\n```shell\n# pip\npip install django-hogwarts\n\n# poetry\npoetry add django-hogwarts\n```\n\nadd `hogwarts` to your `INSTALLED_APPS`:\n``` python\nINSTALLED_APPS = [\n    ...\n    "hogwarts"\n]\n```\n\n## Usage\n> Check [this](./docs/conventions.md) to know what urls will be generated\n### Generate urls.py\nGenerates paths for views from views.py\n```\npython manage.py genurls <your-app-name>\n```\n\nArguments:\n- `--force-app-name`, `fan` override app_name variable in urls.py \n- `--override`, `-o` fully overrides existing code in urls.py (previous code will be deleted)\n- `--single-import`, `-s` instead of importing individual view, imports just module`from . import views`\n\n### Generate views.py\nGenerates create, update, detail, list views for model.\nCheckout the [demo](./docs/gen_views_example.md)\n```\npython manage.py genviews <your-app-name> <model-name>\n```\nArguments\n- `--smart-mode`, `-s` adds login required, sets user for CreateView and checks if client is owner of object in UpdateView\n- `--model-is-namespace`, `-mn` adds success_url with name model as [namespace](https://docs.djangoproject.com/en/4.2/topics/http/urls/#url-namespaces)\n- `--file`, `-f` specify view file (example: "views/posts_view.py" or "new_views.py") in your app\n\n### Generate templates\nGenerates templates from `template_name`s from views from given app\n\n**[django-crispy-forms](https://github.com/django-crispy-forms/django-crispy-forms) and\n[crispy-bootstrap5](https://github.com/django-crispy-forms/crispy-bootstrap5) packages are required**\n\n``` \npython manage.py gentemplates <your-app-name>\n```\n\nWant to create own scaffolding templates? \n1. create folder, copy and customize from [this templates](https://github.com/adiletto64/django-hogwarts/tree/master/hogwarts/scaffold)\n2. add that folder to setting `HOGWARTS_SCAFFOLD_FOLDER = "<your-folder>"`\n\n### Scaffolding\n\nGenerates views, urls and templates for given app (every model in app)\n\n``` \npython manage.py scaffold <your-app-name>\n```\n\n\n## Roadmap\n- tests generator\n- maybe rest-framework support (let me know in issues)\n\n\n',
    'author': 'adiletto64',
    'author_email': 'adiletdj19@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/adiletto64/django-hogwarts',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
