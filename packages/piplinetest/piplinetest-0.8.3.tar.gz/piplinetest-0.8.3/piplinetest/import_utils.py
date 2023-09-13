import importlib


def import_lib(lib_path: str):
    module_path, method_name = lib_path.split(":")
    return getattr(importlib.import_module(module_path), method_name)
