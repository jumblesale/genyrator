from enum import Enum

import attr
from typing import List, Optional, NewType, Union, Tuple, Dict, NamedTuple, Set

from genyrator.entities.Relationship import Relationship
from genyrator.entities.Column import Column, create_column, IdentifierColumn, create_identifier_column
from genyrator.inflector import pythonize, pluralize, dasherize, humanize, to_class_name, to_json_case
from genyrator.types import string_to_type_option

APIPath = NamedTuple(
    'APIPath',
    [('joined_entities', List[str]),
     ('route',           str),
     ('endpoint',        str),
     ('class_name',      str),
     ('python_name',     str),
     ('property_name',   str), ]
)
Property = NewType('Property', Union[Column, Relationship, IdentifierColumn])
APIPaths = NewType('APIPaths', List[APIPath])


class OperationsOption(Enum):
    create_with_id =    'create_with_id'
    create_without_id = 'create_without_id'
    update =            'update'
    get_one =           'get'
    get_all =           'get_all'
    delete =            'delete'
    delete_all =        'delete_all'


all_operations: Set[OperationsOption] = set([o for o in OperationsOption])


@attr.s
class Entity(object):
    python_name:          str =                   attr.ib()
    class_name:           str =                   attr.ib()
    display_name:         str =                   attr.ib()
    identifier_column:    IdentifierColumn =      attr.ib()
    columns:              List[Column] =          attr.ib()
    relationships:        List[Relationship] =    attr.ib()
    table_name:           Optional[str] =         attr.ib()
    uniques:              Set[List[str]] =        attr.ib()
    max_property_length:  int =                   attr.ib()
    plural:               str =                   attr.ib()
    dashed_name:          str =                   attr.ib()
    resource_namespace:   str =                   attr.ib()
    resource_path:        str =                   attr.ib()
    table_args:           str =                   attr.ib()
    operations:           Set[OperationsOption] = attr.ib()
    api_paths:            Optional[APIPaths] =    attr.ib()


def create_entity(
        class_name:         str,
        identifier_column:  IdentifierColumn,
        columns:            List[Column],
        operations:         Set[OperationsOption],
        relationships:      List[Relationship]=list(),
        uniques:            List[List[str]]=list(),
        display_name:       Optional[str]=None,
        table_name:         Optional[str]=None,
        plural:             Optional[str]=None,
        resource_namespace: Optional[str]=None,
        resource_path:      Optional[str]=None,
        api_paths:          Optional[APIPaths]=None,
) -> Entity:
    python_name = pythonize(class_name)
    columns = [identifier_column, *columns]
    uniques = [[identifier_column.python_name], *uniques]
    max_property_length = _calculate_max_property_length(
        identifier_column, columns, relationships
    )
    return Entity(
        class_name=class_name,
        python_name=python_name,
        identifier_column=identifier_column,
        columns=columns,
        max_property_length=max_property_length,
        relationships=relationships,
        display_name=display_name if display_name is not None else humanize(class_name),
        table_name=table_name if table_name is not None else None,
        uniques=uniques,
        plural=plural if plural is not None else pluralize(python_name),
        resource_namespace=resource_namespace if resource_namespace is not None else pluralize(python_name),
        resource_path=resource_path if resource_path is not None else '/',
        dashed_name=dasherize(python_name),
        table_args=_convert_uniques_to_table_args_string(uniques),
        operations=operations,
        api_paths=api_paths if api_paths is not None else [],
    )


def create_entity_from_type_dict(
        class_name:             str,
        identifier_column_name: str,
        type_dict:              Dict,
        foreign_keys:           Set[Tuple[str, str]]=set(),
        indexes:                Set[str]=set(),
        relationships:          Optional[List[Relationship]]=None,
        table_name:             Optional[str]=None,
        uniques:                Optional[List[List[str]]]=None,
        api_paths:              Optional[APIPaths]=None,
) -> Entity:
    columns = []
    foreign_keys_dict = {}
    for fk_key, fk_value in foreign_keys:
        foreign_keys_dict[fk_key] = '{table}.{fk_column}'.format(
            table=fk_value, fk_column=pythonize(fk_key)
        )
    identifier_column = None
    for k, v in type_dict.items():
        nullable = v.endswith('?')
        v = v.replace('?', '')
        type_option = string_to_type_option(v)
        foreign_key = foreign_keys_dict[k] if k in foreign_keys_dict else None
        index = k in indexes
        if k == identifier_column_name:
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
    return create_entity(
        class_name=class_name,
        identifier_column=identifier_column,
        columns=columns,
        operations=all_operations,
        relationships=relationships if relationships else [],
        table_name=table_name,
        uniques=uniques if uniques else [],
        api_paths=api_paths,
    )


def create_api_path(
        joined_entities: List[str],
        route:           str,
        endpoint:        Optional[str]=None,
        class_name:      Optional[str]=None,
        property_name:   Optional[str]=None,
) -> APIPath:
    python_name = pythonize(joined_entities[-1])
    property_name = property_name if property_name else to_json_case(python_name)
    return APIPath(joined_entities, route,
                   endpoint if endpoint else '-'.join(joined_entities),
                   class_name=class_name if class_name else to_class_name(python_name),
                   python_name=python_name, property_name=property_name)


def _convert_uniques_to_table_args_string(uniques: List[List[str]]) -> str:
    unique_constraints = []
    for unique_columns in uniques:
        unique_constraints.append('UniqueConstraint({}, )'.format(
            ', '.join(["'{}'".format(uc) for uc in unique_columns])
        ))
    return '({}, )'.format(', '.join(unique_constraints))


def _calculate_max_property_length(
        identifier_column: IdentifierColumn,
        columns:           List[Column],
        relationships:     List[Relationship],
) -> int:
    return max(
        len(identifier_column.python_name),
        *[len(x.python_name) for x in columns],
        *[len(x.property_name) for x in relationships],
    )


def add_api_paths_to_entity(
        entity:    Entity,
        api_paths: APIPaths,
) -> Entity:
    args = entity.__dict__
    args['api_paths'] = api_paths
    return Entity(**args)


def add_relationship_to_entity(
        entity:       Entity,
        relationship: Relationship,
) -> Entity:
    args = entity.__dict__
    args['relationships'].append(relationship)
    args['max_property_length'] = _calculate_max_property_length(
        entity.identifier_column,
        entity.columns,
        args['relationships'],
    )
    return Entity(**args)
