from typing import Any, Mapping

from sqlalchemy.ext.declarative import DeclarativeMeta

from bookshop.domain.types import DomainModel


def convert_properties_to_sqlalchemy_properties(
        model:           DomainModel,
        joined_entities: Mapping[str, int],
        data:            Mapping[str, Any],
) -> Mapping[str, Any]:
    result = {}

    for k, v in data.items():
        if k == 'id':
            result[model.identifier_column_name] = data[k]
        elif k in joined_entities:
            entity = joined_entities[k]
            result[model.external_identifier_map[k].source_foreign_key_column] = entity
        else:
            result[k] = v
    return result


def convert_sqlalchemy_properties_to_dict_properties(
        domain_model:     DomainModel,
        sqlalchemy_model: DeclarativeMeta,
        data:             Mapping[str, Any],
) -> Mapping[str, Any]:
    for property in domain_model.property_keys:
        ...
