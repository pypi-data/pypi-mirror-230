from dataclasses import dataclass


@dataclass
class Path:
    path_url: str
    view: str
    path_name: str


def extract_paths(code: str):
    lines = code.strip().split("\n")
    extracted_list: list[Path] = []

    for line in lines:
        if "path(" in line:
            parts = line.split('"')
            first_arg = parts[1]
            second_arg = parts[2].split(',')[1].strip()
            if second_arg.endswith(".as_view()"):
                second_arg = second_arg.split(".")[-2]

            third_arg = parts[3]
            extracted_list.append(Path(first_arg, second_arg, third_arg))

    return extracted_list


def append_path_to_urls_code(code: str, path: str):
    closing_bracket_index = code.rfind(']')

    if closing_bracket_index == -1:
        raise ValueError(f"code {code} does not have closing ']' symbol")

    return code[:closing_bracket_index] + f"    {path}\n]"
