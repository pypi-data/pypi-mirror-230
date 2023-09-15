import pathlib

MAIN_STR = "__main__"


def replace__main__with_real_name(name: str, file_path: str):
    module_name = ".".join(pathlib.Path(file_path).with_suffix("").parts)
    name = name.replace(MAIN_STR, module_name)
    return name
