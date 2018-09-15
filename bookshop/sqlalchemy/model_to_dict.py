from typing import List, Mapping, Any, Optional, Union

from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.collections import InstrumentedList

from bookshop.core.convert_dict import python_dict_to_json_dict
from bookshop.domain.types import DomainModel
from bookshop.sqlalchemy.convert_between_models import convert_sqlalchemy_model_to_domain_model


def model_to_dict(
    sqlalchemy_model: DeclarativeMeta,
    paths:            List[str] = list(),
) -> Mapping[str, Any]:
    eager_relationships = {}
    domain_model = convert_sqlalchemy_model_to_domain_model(sqlalchemy_model)
    # always hydrate eager relationships
    for relationship in domain_model.eager_relationships:
        relationship_model = getattr(sqlalchemy_model, relationship)
        eager_relationships[relationship] = _recurse_on_model_or_list(
            model_or_list=relationship_model,
            return_immediately=True,
        )
    return {
        **eager_relationships,
        **_model_to_dict(
            sqlalchemy_model=sqlalchemy_model,
            paths=paths,
        ),
    }


def _model_to_dict(
    sqlalchemy_model:   Optional[DeclarativeMeta],
    paths:              List[str] = list(),
    return_immediately: bool = False,
) -> Optional[Mapping[str, Any]]:
    """
    recursively convert a sql alchemy result into a dictionary
    """
    if sqlalchemy_model is None:
        return None
    domain_model = convert_sqlalchemy_model_to_domain_model(sqlalchemy_model)
    serialized_data = _serialize_data(
        domain_model=domain_model,
        sqlalchemy_model=sqlalchemy_model,
    )
    if not paths or return_immediately is True:
        return python_dict_to_json_dict(serialized_data)
    next_path = paths[0]
    next_relationship = getattr(sqlalchemy_model, next_path)
    next_key = next_path
    serialized_data[next_key] = _recurse_on_model_or_list(
        model_or_list=next_relationship,
        paths=paths,
    )
    return python_dict_to_json_dict(serialized_data)


def _serialize_data(
    domain_model:     DomainModel,
    sqlalchemy_model: DeclarativeMeta,
) -> Mapping[str, Any]:
    serialized_data = {}
    for domain_property in domain_model.property_keys:
        if domain_property in domain_model.json_translation_map:
            dict_key = domain_model.json_translation_map[domain_property]
        else:
            dict_key = domain_property
        value = getattr(sqlalchemy_model, domain_property)
        serialized_data[dict_key] = value
    return serialized_data


def _recurse_on_model_or_list(
    model_or_list:      Union[InstrumentedList, DeclarativeMeta],
    paths:              List[str]=list(),
    return_immediately: bool=False,
) -> Optional[Union[List[Mapping[str, Any]], Mapping[str, Any]]]:
    next_paths = paths[1:] if paths else []
    if type(model_or_list) is InstrumentedList:
        return [
            python_dict_to_json_dict(_model_to_dict(
                sqlalchemy_model=nr,
                paths=next_paths,
                return_immediately=return_immediately,
            ))
            for nr in model_or_list
        ]
    else:
        return python_dict_to_json_dict(
            _model_to_dict(
                sqlalchemy_model=model_or_list,
                paths=next_paths,
                return_immediately=return_immediately,
            ))
