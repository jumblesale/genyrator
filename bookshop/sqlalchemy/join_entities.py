from typing import Any, Mapping

from bookshop.core.convert_case import to_json_name
from bookshop.domain.types import DomainModel


def create_joined_entity_map(
    domain_model: DomainModel,
    data:         Mapping[str, Any]
) -> Mapping[str, Any]:
    joined_entities = {}
    for relationship_name, relationship in domain_model.relationship_map.items():
        json_relationship_name = to_json_name(relationship_name)
        if json_relationship_name not in data:
            continue
        filter_kwargs = {relationship.target_identifier_column: data[json_relationship_name]}
        joined_entities[relationship_name] = relationship.target.query.filter_by(**filter_kwargs).one()
    return joined_entities