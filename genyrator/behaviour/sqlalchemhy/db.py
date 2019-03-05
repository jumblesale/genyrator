from importlib import import_module


def get_db_instance(
        module_name:   str,
        variable_name: str,
):
    module = import_module(module_name)
    instance = getattr(module, variable_name)
    return instance
