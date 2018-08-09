from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.collections import InstrumentedList
from bookshop.core.convert_dict import python_dict_to_json_dict


def model_to_dict(model: DeclarativeMeta, paths=list()):
    """
    recursively convert a sql alchemy result into a dictionary
    :param model:
    :param paths:
    :return:
    """
    serialized_data = {}
    for c in model.__table__.columns:
        if c.primary_key:
            continue
        key = c.key
        value = getattr(model, c.key)
        serialized_data[key] = value
    if not paths:
        return python_dict_to_json_dict(serialized_data)
    next_path = paths[0]
    next_relationship = getattr(model, next_path)
    next_key = next_path
    if type(next_relationship) is InstrumentedList:
        serialized_data[next_key] = [
            python_dict_to_json_dict(model_to_dict(nr, paths[1:])) for nr in next_relationship
        ]
    else:
        serialized_data[next_key] = python_dict_to_json_dict(model_to_dict(next_relationship, paths[1:]))
    return serialized_data
