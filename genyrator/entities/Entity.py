from enum import Enum

import attr
from typing import List, Optional, NewType, Union, NamedTuple, Set

from genyrator.entities.Relationship import Relationship
from genyrator.entities.Column import Column, IdentifierColumn
from genyrator.inflector import pythonize, pluralize, dasherize, humanize, to_class_name, to_json_case

APIPath = NamedTuple(
    'APIPath',
    [('joined_entities', List[str]),
     ('route',           str),
     ('endpoint',        str),
     ('class_name',      str),
     ('python_name',     str),
     ('property_name',   str), ]
)
Property = Union[Column, Relationship, IdentifierColumn]

ImportAlias = NamedTuple(
    'ImportAlias',
    [('class_name',    str),
     ('module_import', str), ]
)

AdditionalProperty = NamedTuple(
    'AdditionalProperty',
    [('python_name', str),
     ('value',       str), ]
)


class OperationOption(Enum):
    create_with_id =    'create_with_id'
    create_without_id = 'create_without_id'
    update =            'update'
    patch =             'patch'
    get_one =           'get_one'
    get_all =           'get_all'
    delete_one =        'delete_one'
    delete_all =        'delete_all'


def string_to_operation_option(option: str) -> OperationOption:
    return {
        "create_with_id":    OperationOption.create_with_id,
        "create_without_id": OperationOption.create_without_id,
        "update":            OperationOption.update,
        "patch":             OperationOption.patch,
        "get_one":           OperationOption.get_one,
        "get_all":           OperationOption.get_all,
        "delete_one":        OperationOption.delete_one,
        "delete_all":        OperationOption.delete_all,
    }[option]


all_operations: Set[OperationOption] = set([o for o in OperationOption])


@attr.s
class Entity(object):
    python_name:           str =                      attr.ib()
    class_name:            str =                      attr.ib()
    display_name:          str =                      attr.ib()
    identifier_column:     IdentifierColumn =         attr.ib()
    columns:               List[Column] =             attr.ib()
    relationships:         List[Relationship] =       attr.ib()
    table_name:            Optional[str] =            attr.ib()
    uniques:               List[List[str]] =          attr.ib()
    max_property_length:   int =                      attr.ib()
    plural:                str =                      attr.ib()
    dashed_plural:         str =                      attr.ib()
    dashed_name:           str =                      attr.ib()
    resource_namespace:    str =                      attr.ib()
    resource_path:         str =                      attr.ib()
    table_args:            str =                      attr.ib()
    operations:            Set[OperationOption] =     attr.ib()
    api_paths:             Optional[List[APIPath]] =  attr.ib()
    supports_put:          bool =                     attr.ib()
    supports_get_one:      bool =                     attr.ib()
    supports_get_all:      bool =                     attr.ib()
    supports_post:         bool =                     attr.ib()
    supports_patch:        bool =                     attr.ib()
    supports_delete_one:   bool =                     attr.ib()
    supports_delete_all:   bool =                     attr.ib()
    model_alias:           Optional[ImportAlias] =    attr.ib()
    additional_properties: List[AdditionalProperty] = attr.ib()

    @property
    def has_joined_entities(self):
        return any(
            len(api_path.joined_entities) > 0 for api_path in self.api_paths
        )


def create_entity(
        class_name:         str,
        identifier_column:  IdentifierColumn,
        columns:            List[Column],
        relationships:      List[Relationship] = list(),
        uniques:            List[List[str]] = list(),
        operations:         Optional[Set[OperationOption]] = None,
        display_name:       Optional[str] = None,
        table_name:         Optional[str] = None,
        plural:             Optional[str] = None,
        dashed_plural:      Optional[str] = None,
        resource_namespace: Optional[str] = None,
        resource_path:      Optional[str] = None,
        api_paths:          Optional[List[APIPath]] = None,
        model_alias:        Optional[ImportAlias] = None,
        additional_properties: Optional[List[AdditionalProperty]] = None
) -> Entity:
    """Return a fully configured Entity

    The returned Entity is configured with columns and relationships.

    Args:
        class_name:          The class name (eg BookClub) used for the SQLAlchemy
                             and RESTPlus models

        identifier_column:   The column used to identify the entity in the URL. Note;
                             this is not the primary key of the SQLAlchemy model and therefore
                             is not used for joins.

        columns:             All columns except for the internally generated primary key.
                             This must includes the identifier column and any columns
                             required for relationships.

        relationships:       The relationships between entities. This means just SQLAlchemy
                             relationships unless the relationship is non-lazy in which case
                             it will also appear in the JSON response.

        uniques:             A list of list of column names that require unique indexes.
                             The identifier column does not need to appear in here.

        operations:          HTTP actions which should be generated for this entity.

        display_name:        Human readable name (eg Book Club). Has sensible default.

        table_name:          The SQLAlchemy table. Has sensible default.

        plural:              The plural form of the entity name used in method names
                             (eg book_clubs). Has sensible default.

        dashed_plural:       The plural form of the entity name used in URIs and
                             RESTPlus resource IDs (eg book-clubs). Has sensible default.

        resource_namespace:  RESTPlus namespace resource name for entity (eg BookClub). Has sensible default.

        resource_path:       RESTPlus namespace path. Has sensible default.

        api_paths:           List of class names for which RESTPlus routes should
                             be created. A relationship must exist for the path.
                             This is only needed for lazy relationships.

        model_alias:         Override the SQLAlchemy model used in the RESTPlus routes.
                             Use this if you want to extend the generated SQLAlchemy model.

        additional_properties: Key value pairs to be added to the SQLAlchemy model.
                               They will end up in the model as `key = value`.
    """
    operations = operations if operations is not None else all_operations
    python_name = pythonize(class_name)
    columns = [identifier_column, *columns]
    if [identifier_column.python_name] not in uniques:
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
        dashed_plural=dashed_plural if dashed_plural is not None else dasherize(pluralize(python_name)),
        resource_namespace=resource_namespace if resource_namespace is not None else pluralize(python_name),
        resource_path=resource_path if resource_path is not None else '/',
        dashed_name=dasherize(python_name),
        table_args=_convert_uniques_to_table_args_string(uniques),
        operations=operations if operations is not None else all_operations,
        api_paths=api_paths if api_paths is not None else [],
        supports_put=OperationOption.create_with_id in operations,
        supports_get_one=OperationOption.get_one in operations,
        supports_get_all=OperationOption.get_all in operations,
        supports_post=OperationOption.create_without_id in operations,
        supports_patch=OperationOption.patch in operations,
        supports_delete_one=OperationOption.delete_one in operations,
        supports_delete_all=OperationOption.delete_all in operations,
        model_alias=model_alias,
        additional_properties=additional_properties if additional_properties is not None else [],
    )


def create_api_path(
        joined_entities: List[str],
        route:           str,
        endpoint:        Optional[str] = None,
        class_name:      Optional[str] = None,
        property_name:   Optional[str] = None,
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
        api_paths: List[APIPath],
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


def create_additional_property(
        property_name:  str,
        property_value: str,
) -> AdditionalProperty:
    return AdditionalProperty(python_name=property_name, value=property_value)
