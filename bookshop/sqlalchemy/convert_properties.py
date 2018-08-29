from typing import Any, Mapping

from sqlalchemy.ext.declarative import DeclarativeMeta

from bookshop.domain.types import DomainModel


def convert_properties_to_sqlalchemy_properties(
        model:           DomainModel,
        joined_entities: Mapping[str, DeclarativeMeta],
        data:            Mapping[str, Any],
) -> Mapping[str, Any]:
    result = {}

    for k, v in data.items():
        if k == 'id':
            result[model.identifier_column_name] = data[k]
        elif k in joined_entities:
            entity = joined_entities[k]
            result[model.relationship_map[k].source_foreign_key_column] = getattr(entity, 'id')
        else:
            result[k] = v
    return result
