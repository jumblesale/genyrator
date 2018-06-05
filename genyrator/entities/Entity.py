import attr
from typing import List, Optional, NewType, Union, Tuple, Dict, NamedTuple, Set

from genyrator.entities.Relationship import Relationship
from genyrator.entities.Column import Column, create_column, IdentifierColumn, create_identifier_column
from genyrator.inflector import pythonize, pluralize, dasherize, to_class_name
from genyrator.types import string_to_type_option

APIPath = NamedTuple(
    'APIPath',
    [('joined_entities', List[str]),
     ('route',           str),
     ('endpoint',        str),
     ('class_name',      str),
     ('python_name',     str), ]
)
Property = NewType('Property', Union[Column, Relationship, IdentifierColumn])
APIPaths = NewType('APIPaths', List[APIPath])


@attr.s
class Entity(object):
    python_name:          str =                attr.ib()
    class_name:           str =                attr.ib()
    identifier_column:    IdentifierColumn =   attr.ib()
    columns:              List[Column] =       attr.ib()
    relationships:        List[Relationship] = attr.ib()
    table_name:           Optional[str] =      attr.ib()
    uniques:              Set[List[str]] =    attr.ib()
    properties:           List[Property] =     attr.ib()
    max_property_length:  int =                attr.ib()
    plural:               str =                attr.ib()
    dashed_name:          str =                attr.ib()
    resource_namespace:   str =                attr.ib()
    resource_path:        str =                attr.ib()
    table_args:           str =                attr.ib()
    api_paths:            Optional[APIPaths] = attr.ib()


def create_entity(
        class_name:         str,
        identifier_column:  Column,
        columns:            List[Column],
        relationships:      List[Relationship]=list(),
        uniques:            List[List[str]]=list(),
        table_name:         Optional[str]=None,
        plural:             Optional[str]=None,
        resource_namespace: Optional[str]=None,
        resource_path:      Optional[str]=None,
        api_paths:          Optional[APIPaths]=None,
) -> Entity:
    properties: List[Property] = columns + relationships + [identifier_column]
    python_name = pythonize(class_name)
    columns = [identifier_column] + columns
    uniques = [[identifier_column.python_name]] + uniques
    return Entity(
        class_name=class_name,
        python_name=python_name,
        identifier_column=identifier_column,
        columns=columns,
        max_property_length=(max(*[len(x.python_name) for x in properties])),
        relationships=relationships,
        table_name=table_name if table_name else None,
        uniques=uniques,
        properties=properties,
        plural=plural if plural else pluralize(python_name),
        resource_namespace=resource_namespace if resource_namespace else pluralize(python_name),
        resource_path=resource_path if resource_path else '/',
        dashed_name=dasherize(class_name),
        table_args=_convert_uniques_to_table_args_string(uniques),
        api_paths=api_paths if api_paths else [],
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
        type_option = string_to_type_option(v)
        foreign_key = foreign_keys_dict[k] if k in foreign_keys_dict else None
        index = k in indexes
        if k == identifier_column_name:
            identifier_column = create_identifier_column(k, type_option)
            continue
        columns.append(
            create_column(k, type_option, foreign_key, index)
        )
    return create_entity(
        class_name=class_name,
        identifier_column=identifier_column,
        columns=columns,
        relationships=relationships,
        table_name=table_name,
        uniques=uniques,
        api_paths=api_paths,
    )


def create_api_path(
        joined_entities: List[str],
        route:           str,
        endpoint:        Optional[str]=None,
        class_name:      Optional[str]=None,
) -> APIPath:
    python_name = '_'.join(joined_entities)
    return APIPath(joined_entities, route,
                   endpoint if endpoint else '-'.join(joined_entities),
                   class_name=class_name if class_name else to_class_name(python_name),
                   python_name=python_name, )


def _convert_uniques_to_table_args_string(uniques: List[List[str]]) -> str:
    unique_constraints = []
    for unique_columns in uniques:
        unique_constraints.append('UniqueConstraint({}, )'.format(
            ', '.join(["'{}'".format(uc) for uc in unique_columns])
        ))
    return '({}, )'.format(', '.join(unique_constraints))
