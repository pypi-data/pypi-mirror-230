import ast


def to_plural(string: str):
    if string.endswith("s"):
        return string
    elif string.endswith("y"):
        return string[:-1] + "ies"
    else:
        return string + "s"


def get_imports_list(path: str) -> list[str]:
    with open(path, "r") as file:
        tree = ast.parse(file.read())

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports.append(alias.name)

    return imports


def get_classes_list(path: str) -> list[str]:
    with open(path, "r") as file:
        tree = ast.parse(file.read())

    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)

    return classes


def code_strip(code: str):
    if code[0] == '\n':
        code = code[1:]

    spaces = 0
    code = code.split("\n")

    for i in code[0]:
        if i == " ":
            spaces += 1
        else:
            break

    for i in range(len(code)):
        code[i] = code[i][spaces:].rstrip()

    return "\n".join(code)


def remove_empty_lines(text: str):
    lines = text.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]  # DON'T TOUCH THIS LINE
    return '\n'.join(non_empty_lines)


def parse_class_names(code):
    class_names = []

    tree = ast.parse(code)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_names.append(node.name)

    return class_names


def remove_imports(code):
    lines = code.split('\n')
    new_lines = []
    inside_import_block = False

    for line in lines:
        if line.strip().startswith("import ") or line.strip().startswith("from "):
            inside_import_block = True
        elif inside_import_block and not line.strip():
            inside_import_block = False
            continue

        if not inside_import_block:
            new_lines.append(line)

    new_code = '\n'.join(new_lines)
    return new_code
