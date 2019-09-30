from typing import Set, Dict, Tuple, List, Optional

from genyrator import Relationship, string_to_type_option
from genyrator.errors import GenyratorError
from genyrator.entities.Column import ForeignKeyRelationship, create_column, create_identifier_column
from genyrator.entities.Entity import APIPath, OperationOption, ImportAlias, AdditionalProperty, Entity, create_entity, \
    all_operations
from genyrator.inflector import pythonize


def create_entity_from_type_dict(
        class_name:             str,
        identifier_column_name: str,
        type_dict:              Dict,
        foreign_keys:           Set[Tuple[str, str, str]] = set(),
        indexes:                Set[str] = set(),
        operations:             Optional[Set[OperationOption]] = None,
        relationships:          Optional[List[Relationship]] = None,
        table_name:             Optional[str] = None,
        uniques:                Optional[List[List[str]]] = None,
        api_paths:              Optional[List[APIPath]] = None,
        model_alias:            Optional[ImportAlias] = None,
        additional_properties:  Optional[List[AdditionalProperty]] = None,
) -> Entity:
    columns = []
    foreign_keys_dict = {}
    for fk_key, fk_value, fk_type in foreign_keys:
        foreign_keys_dict[fk_key] = ForeignKeyRelationship(
            f'{pythonize(fk_value)}', string_to_type_option(fk_type)
        )
    identifier_column = None
    for k, v in type_dict.items():
        nullable = v.endswith('?')
        v = v.replace('?', '')
        type_option = string_to_type_option(v)
        foreign_key = foreign_keys_dict[k] if k in foreign_keys_dict else None
        index = k in indexes
        if pythonize(k) == pythonize(identifier_column_name):
            identifier_column = create_identifier_column(k, type_option)
        else:
            column = create_column(
                name=k,
                type_option=type_option,
                foreign_key_relationship=foreign_key,
                index=index,
                nullable=nullable,
                identifier=False
            )
            columns.append(column)

    if identifier_column is None:
        raise GenyratorError('Entity must have an identifier column')

    return create_entity(
        class_name=class_name,
        identifier_column=identifier_column,
        columns=columns,
        operations=operations if operations is not None else all_operations,
        relationships=relationships if relationships else [],
        table_name=table_name,
        uniques=uniques if uniques else [],
        api_paths=api_paths,
        model_alias=model_alias,
        additional_properties=additional_properties if additional_properties is not None else [],
    )
