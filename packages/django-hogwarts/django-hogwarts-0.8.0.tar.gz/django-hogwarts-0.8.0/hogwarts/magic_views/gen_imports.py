import ast
from typing import Tuple

Imports = list[Tuple[str, str]]


class ImportsGenerator:
    def __init__(self):
        self.imports: Imports = []

    def add(self, module, obj):
        if not self.exists(obj):
            self.imports.append((module, obj))

    def exists(self, obj: str):
        return any(i[1] == obj for i in self.imports)

    def add_bulk(self, module, objs: list[str]):
        for obj in objs:
            self.add(module, obj)

    def gen(self):
        merged_imports = self.get_merge_imports()
        result = ""
        for module, objs in merged_imports.items():
            if module is None:
                result += f"import {', '.join(objs)}\n"
            else:
                result += f"from {module} import {', '.join(objs)}\n"

        return result

    def get_merge_imports(self):
        merged_imports = {}
        for module, obj in self.imports:
            if module not in merged_imports.keys():
                merged_imports[module] = [obj]
            else:
                merged_imports[module].append(obj)
        return merged_imports

    def parse_imports(self, code):
        imports = []
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.add(None, alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module
                for alias in node.names:
                    if module:
                        self.add(f"{'.' * node.level}{module}", alias.name)

        return imports

    @property
    def imported_classes(self):
        for _import in self.imports:
            yield _import[1]


class ViewImportsGenerator(ImportsGenerator):
    def add_login_required(self):
        self.add("django.contrib.auth.mixins", "LoginRequiredMixin")

    def add_user_test(self):
        self.add("django.contrib.auth.mixins", "UserPassesTestMixin")

    def add_reverse(self):
        self.add("django.shortcuts", "reverse")

    def add_reverse_lazy(self):
        self.add("django.shortcuts", "reverse_lazy")
