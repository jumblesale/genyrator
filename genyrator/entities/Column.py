from typing import Optional
import attr
from genyrator.inflector import pythonize, to_class_name, to_json_case
from genyrator.types import (
    SqlAlchemyTypeOption, PythonTypeOption, TypeOption, type_option_to_sqlalchemy_type,
    type_option_to_python_type, type_option_to_default_value, RestplusTypeOption,
    type_option_to_restplus_type)


@attr.s
class Column(object):
    python_name:        str =                  attr.ib()
    class_name:         str =                  attr.ib()
    json_property_name: str =                  attr.ib()
    type_option:        TypeOption =           attr.ib()
    sqlalchemy_type:    SqlAlchemyTypeOption = attr.ib()
    python_type:        PythonTypeOption =     attr.ib()
    restplus_type:      RestplusTypeOption =   attr.ib()
    default:            str =                  attr.ib()
    index:              bool =                 attr.ib()
    nullable:           bool =                 attr.ib()


@attr.s
class ForeignKey(Column):
    relationship: str = attr.ib()


@attr.s
class IdentifierColumn(Column):
    ...


def create_identifier_column(
        name:                     str,
        type_option:              TypeOption,
) -> IdentifierColumn:
    column: IdentifierColumn = create_column(
        name, type_option, index=True, nullable=False, identifier=True,
    )
    return column


def create_column(
        name:                     str,
        type_option:              TypeOption,
        foreign_key_relationship: Optional[str]=None,
        index:                    bool=False,
        nullable:                 bool=True,
        identifier:               bool=False,
) -> Column:
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
        "type_option":        type_option,
        "sqlalchemy_type":    type_option_to_sqlalchemy_type(type_option),
        "python_type":        type_option_to_python_type(type_option),
        "restplus_type":      type_option_to_restplus_type(type_option),
        "default":            type_option_to_default_value(type_option),
        "index":              index,
        "nullable":           nullable,
    }
    if foreign_key_relationship is not None:
        args["relationship"] = foreign_key_relationship
    return constructor(**args)
