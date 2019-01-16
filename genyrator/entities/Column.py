from typing import Optional, Union, NamedTuple
import attr
from genyrator.inflector import pythonize, to_class_name, to_json_case, humanize
from genyrator.types import (
    SqlAlchemyTypeOption, PythonTypeOption, TypeOption, type_option_to_sqlalchemy_type,
    type_option_to_python_type, type_option_to_default_value, RestplusTypeOption,
    type_option_to_restplus_type,
    type_option_to_faker_method)

ForeignKeyRelationship = NamedTuple(
    'ForeignKeyRelationship', [
        ('target_entity',                        str),
        ('target_entity_identifier_column_type', TypeOption), ]
)


@attr.s
class Column(object):
    python_name:        str =                  attr.ib()
    class_name:         str =                  attr.ib()
    display_name:       str =                  attr.ib()
    alias:              str =                  attr.ib()
    json_property_name: str =                  attr.ib()
    type_option:        TypeOption =           attr.ib()
    faker_method:       str =                  attr.ib()
    sqlalchemy_type:    SqlAlchemyTypeOption = attr.ib()
    python_type:        PythonTypeOption =     attr.ib()
    restplus_type:      RestplusTypeOption =   attr.ib()
    default:            str =                  attr.ib()
    index:              bool =                 attr.ib()
    nullable:           bool =                 attr.ib()


@attr.s
class ForeignKey(Column):
    relationship:         str = attr.ib()
    target_restplus_type: str = attr.ib()


@attr.s
class IdentifierColumn(Column):
    ...


def create_column(
        name:                     str,
        type_option:              TypeOption,
        index:                    bool = False,
        nullable:                 bool = True,
        identifier:               bool = False,
        display_name:             Optional[str] = None,
        alias:                    Optional[str] = None,
        foreign_key_relationship: Optional[ForeignKeyRelationship] = None,
        faker_method:             Optional[str] = None,
) -> Union[Column, ForeignKey]:
    """Return a column to be attached to an entity

    Args:
        name:        The property name on the SQLAlchemy model

        type_option: The type of the column.

        index:       Whether to create a database index for the column.

        nullable:    Whether to allow the column to be nullable in the database.

        identifier:  If set to True all other args will be ignored and this will
                     created as an identifier column. See: create_identifier_column

        display_name: Human readable name intended for use in UIs.

        alias:        Column name to be used the database.

        foreign_key_relationship: The entity this column relates. If this is not
                                  None the result will be a `ForeignKey`.

        faker_method: The method to pass to Faker to provide fixture data for this column.
                      Defaults to the constructor for the type of this column
    """
    if identifier is True:
        constructor = IdentifierColumn
    elif foreign_key_relationship is not None:
        constructor = ForeignKey
    else:
        constructor = Column
    args = {
        "python_name":        pythonize(name),
        "class_name":         to_class_name(name),
        "json_property_name": to_json_case(name),
        "display_name":       display_name if display_name else humanize(name),
        "type_option":        type_option,
        "sqlalchemy_type":    type_option_to_sqlalchemy_type(type_option),
        "python_type":        type_option_to_python_type(type_option),
        "restplus_type":      type_option_to_restplus_type(type_option),
        "default":            type_option_to_default_value(type_option),
        "index":              index,
        "nullable":           nullable,
        "alias":              alias,
        "faker_method":       type_option_to_faker_method(type_option),
    }
    if foreign_key_relationship is not None:
        args['relationship'] = '{}.{}'.format(
            pythonize(foreign_key_relationship.target_entity),
            'id'
        )
        args['target_restplus_type'] = type_option_to_restplus_type(
            foreign_key_relationship.target_entity_identifier_column_type
        )
    return constructor(**args)


def create_identifier_column(
        name:        str,
        type_option: TypeOption,
) -> IdentifierColumn:
    """Return an identifier column for an entity

    The identifier column is not the database primary key for the table.
    The primary key is auto-generated and is always called `id`.

    This identifier column is always unique, indexed and non-nullable.

    Args:
        name:        The property name on the SQLAlchemy model.
        type_option: The type of the column.
    """
    column: IdentifierColumn = create_column(
        name=name, type_option=type_option, index=True, nullable=False,
        identifier=True,
    )
    return column
