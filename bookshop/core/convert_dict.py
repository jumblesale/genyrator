import datetime
from typing import Mapping, Dict, Callable, Any, Iterable, List
from bookshop.core.convert_case import to_json_name, to_python_name


def convert_dict_naming(
    in_dict: Dict,
    fn:      Callable[[str], str],
) -> Mapping[str, Any]:
    out_dict = {}
    for k, v in in_dict.items():
        if type(v) is dict:
            value = convert_dict_naming(v, fn)
        elif type(v) is list or type(v) is set:
            value = convert_iterable_naming(v, fn)
        else:
            value = v
        out_dict[fn(k)] = dict_value_to_json_value(value)
    return out_dict


def convert_iterable_naming(
    in_list: Iterable,
    fn:      Callable[[str], str],
) -> List:
    out_list = []
    for v in in_list:
        if type(v) is dict:
            value = convert_dict_naming(v, fn)
        elif type(v) is list or type(v) is set:
            value = convert_iterable_naming(v, fn)
        else:
            value = v
        out_list.append(dict_value_to_json_value(value))
    return out_list


def python_dict_to_json_dict(python_dict: Mapping[str, Any]) -> Mapping[str, Any]:
    return convert_dict_naming(python_dict, to_json_name)


def json_dict_to_python_dict(json_dict: Mapping[str, Any]) -> Mapping[str, Any]:
    return convert_dict_naming(json_dict, to_python_name)


def dict_value_to_json_value(param: Any) -> Any:
    property_type = type(param)
    if property_type is datetime.datetime or property_type is datetime.date:
        return param.isoformat()
    if param.__class__.__name__ == 'UUID':
        return str(param)
    return param
