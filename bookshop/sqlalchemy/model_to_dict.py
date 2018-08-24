from typing import List

from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.collections import InstrumentedList

from bookshop.core.convert_dict import python_dict_to_json_dict
from bookshop.domain.types import DomainModel


def model_to_dict(
    sql_alchemy_model: DeclarativeMeta,
    domain_model:      DomainModel,
    paths:             List[str] = list(),
):
    """
    recursively convert a sql alchemy result into a dictionary
    """
    serialized_data = {}
    for c in sql_alchemy_model.__table__.columns:
        if c.primary_key:
            continue
        key = c.key
        value = getattr(sql_alchemy_model, c.key)
        serialized_data[key] = value
    if not paths:
        return python_dict_to_json_dict(serialized_data)
    next_path = paths[0]
    next_relationship = getattr(sql_alchemy_model, next_path)
    next_key = next_path
    if type(next_relationship) is InstrumentedList:
        serialized_data[next_key] = [
            python_dict_to_json_dict(model_to_dict(nr, domain_model, paths[1:]))
            for nr in next_relationship
        ]
    else:
        serialized_data[next_key] = python_dict_to_json_dict(
            model_to_dict(next_relationship, domain_model, paths[1:])
        )
    return python_dict_to_json_dict(serialized_data)
