from typing import Any, Mapping, Union, List

from bookshop.core.convert_case import to_json_name
from bookshop.domain.types import DomainModel


def create_joined_entity_map(
    domain_model: DomainModel,
    data:         Mapping[str, Any]
) -> Union[List[str], Mapping[str, Any]]:
    errors = []
    joined_entities = {}
    for external_identifier, relationship in domain_model.external_identifier_map.items():
        json_relationship_name = to_json_name(external_identifier)
        if json_relationship_name not in data:
            continue
        target_identifier_value = data[json_relationship_name]
        filter_kwargs = {relationship.target_identifier_column: target_identifier_value}
        result = relationship.sqlalchemy_model_class.query.filter_by(**filter_kwargs).first()
        if relationship.nullable is False and result is None and target_identifier_value is not None:
            errors.append(
                [f'Could not find {relationship.target_name} with {json_relationship_name} equal to {target_identifier_value}']
            )
        else:
            joined_entities[external_identifier] = result
    return joined_entities if not errors else errors
