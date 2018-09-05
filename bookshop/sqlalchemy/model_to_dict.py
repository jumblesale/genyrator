from typing import List, Mapping, Any, Optional, Tuple

from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy import inspect

from bookshop.core.convert_dict import python_dict_to_json_dict
from bookshop.domain.types import DomainModel


def model_to_dict(
    sqlalchemy_model: Optional[DeclarativeMeta],
    domain_model:     DomainModel,
    paths:            List[Tuple[str, DomainModel]] = list(),
) -> Optional[Mapping[str, Any]]:
    """
    recursively convert a sql alchemy result into a dictionary
    """
    if sqlalchemy_model is None:
        return None
    serialized_data = {}
    for attribute_name in inspect(sqlalchemy_model).attrs.keys():
        value = getattr(sqlalchemy_model, attribute_name)
        if attribute_name not in domain_model.relationship_keys:
            serialized_data[attribute_name] = value
    if not paths:
        return python_dict_to_json_dict(serialized_data)
    next_path, next_domain_model = paths[0]
    next_relationship = getattr(sqlalchemy_model, next_path)
    next_key = next_path
    if type(next_relationship) is InstrumentedList:
        serialized_data[next_key] = [
            python_dict_to_json_dict(model_to_dict(
                sqlalchemy_model=nr,
                domain_model=next_domain_model,
                paths=paths[1:],
            ))
            for nr in next_relationship
        ]
    else:
        serialized_data[next_key] = python_dict_to_json_dict(
            model_to_dict(
                sqlalchemy_model=next_relationship,
                domain_model=next_domain_model,
                paths=paths[1:],
            )
        )
    return python_dict_to_json_dict(serialized_data)
