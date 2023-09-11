from typing import Optional
from rich.console import Console

from ..utils import to_plural, code_strip, remove_empty_lines, parse_class_names, remove_imports
from .gen_imports import ViewImportsGenerator


console = Console()


class ViewGenerator:
    def __init__(
            self,
            model,
            smart_mode=False,
            model_is_namespace=False,
            code: Optional[str] = None
    ):
        self.smart_mode = smart_mode
        self.model_is_namespace = model_is_namespace

        self.model_name = model.__name__
        self.name = model.__name__.lower()
        self.fields = [field.name for field in model._meta.fields if field.editable]
        if "id" in self.fields:
            self.fields.remove("id")

        self.creator_field = None
        self.code = code
        self.merge = code is not None
        self.existing_class_names = []

        if self.code:
            self.existing_class_names = parse_class_names(self.code)

        for field in self.fields:
            if field in ["user", "author", "owner", "creator"]:
                self.fields.remove(field)
                self.creator_field = field
                break

        self.imports_generator = ViewImportsGenerator()
        self.generic_views = []

    def gen(self):
        detail = self.detail()
        _list = self.list()
        create = self.create()
        update = self.update()

        result = code_strip(self.gen_imports())
        if self.merge:
            result += "\n"
            result += remove_imports(self.code)

        for view in [detail, _list, create, update]:
            if view is not None:
                result += f"\n\n{code_strip(view)}"
                console.print(f"generated {view.splitlines()[0]}", style="bright_black")
        return result

    def gen_imports(self):
        if self.merge:
            self.imports_generator.parse_imports(self.code)

        self.imports_generator.add_bulk("django.views.generic", self.generic_views)
        self.imports_generator.add(".models", self.model_name)

        return self.imports_generator.gen()

    def create(self):
        if self.merge and f"{self.model_name}CreateView" in self.existing_class_names:
            return None

        self.generic_views.append("CreateView")
        builder = self.get_builder("create")

        builder.set_fields(self.fields)
        self.set_template(builder, "create")

        if self.smart_mode:
            self.imports_generator.add_login_required()
            builder.set_class("create", ["LoginRequiredMixin"])

            if self.creator_field:
                function = f"""
                def form_valid(self, form):
                    form.instance.{self.creator_field} = self.request.user
                    return super().form_valid(form)
                """
                builder.set_extra_code(code_strip(function))

        if self.model_is_namespace:
            self.imports_generator.add_reverse()
            function = f"""
            def get_success_url(self):
                return reverse("{to_plural(self.name)}:detail", args=[self.object.id])
            """
            builder.set_extra_code(code_strip(function))
        else:
            builder.set_success_url("/")

        return builder.gen()

    def update(self):
        if self.merge and f"{self.model_name}UpdateView" in self.existing_class_names:
            return None

        self.generic_views.append("UpdateView")
        builder = self.get_builder("update")
        builder.set_fields(self.fields)
        self.set_template(builder, "update")

        if self.smart_mode:
            if self.creator_field:
                self.imports_generator.add_user_test()
                builder.set_class("update", ["UserPassesTestMixin"])
                function = """
                def test_func(self):
                    return self.get_object() == self.request.user
                """
                builder.set_extra_code(code_strip(function))
            else:
                self.imports_generator.add_login_required()
                builder.set_class("update", ["LoginRequiredMixin"])

        if self.model_is_namespace:
            self.imports_generator.add_reverse()
            function = f"""
            def get_success_url(self):
                return reverse("{to_plural(self.name)}:detail", args=[self.get_object().id])
            """
            builder.set_extra_code(code_strip(function))
        else:
            builder.set_success_url("/")

        return builder.gen()

    def detail(self):
        if self.merge and f"{self.model_name}DetailView" in self.existing_class_names:
            return None

        self.generic_views.append("DetailView")
        builder = self.get_builder("detail")
        builder.set_context_object_name(self.name)
        self.set_template(builder, "detail")

        return builder.gen()

    def list(self):
        if self.merge and f"{self.model_name}ListView" in self.existing_class_names:
            return None

        self.generic_views.append("ListView")
        builder = self.get_builder("list")
        builder.set_context_object_name(to_plural(self.name))
        self.set_template(builder, "list")

        return builder.gen()

    def get_builder(self, action, mixins=[]):
        builder = ClassViewBuilder(self.model_name)
        builder.set_class(action, mixins)
        builder.set_model()

        return builder

    def set_template(self, builder, action):
        builder.set_template_name(f"{to_plural(self.name)}/{self.name}_{action}.html")


class ClassViewBuilder:
    def __init__(self, model_name):
        self.model_name = model_name
        self.result = {
            "class": "",
            "model": "",
            "fields": "",
            "context_object_name": "",
            "template_name": "",
            "success_url": "",
        }

        self.extra_codes = []

    def set_class(self, action, mixins=[]):
        action = action.capitalize()
        class_name = f"{self.model_name}{action}View"
        inherits = [*mixins, f"{action}View"]

        self.result["class"] = f"class {class_name}({', '.join(inherits)}):\n"

    def set_model(self):
        self.result["model"] = f'    model = {self.model_name}\n'

    def set_fields(self, fields: list[str]):
        fields = [f'"{field}"' for field in fields]
        self.result["fields"] = f"    fields = [{', '.join(fields)}]\n"

    def set_context_object_name(self, name):
        self.result["context_object_name"] = f'    context_object_name = "{name}"\n'

    def set_template_name(self, name):
        self.result["template_name"] = f'    template_name = "{name}"\n'

    def set_success_url(self, url):
        self.result["success_url"] = f'    success_url = "{url}"\n'

    def set_extra_code(self, extra_code):
        extra_code = "\n".join(map(lambda line: " " * 4 + line, extra_code.splitlines()))
        extra_code = remove_empty_lines(extra_code)

        self.extra_codes.append(f"\n{extra_code}\n")

    def gen(self):
        code = ""

        for key in self.result.keys():
            code += self.result[key]

        for extra in self.extra_codes:
            code += extra

        return code
