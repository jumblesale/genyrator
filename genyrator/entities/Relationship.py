from enum import Enum
from typing import Optional
import attr
from genyrator.inflector import pythonize


class JoinOption(Enum):
    to_one =  'to_one'
    to_many = 'to_many'


@attr.s
class Relationship(object):
    python_name:               str =        attr.ib()
    target_entity_class_name:  str =        attr.ib()
    target_entity_python_name: str =        attr.ib()
    property_name:             str =        attr.ib()
    nullable:                  bool =       attr.ib()
    lazy:                      bool =       attr.ib()
    join:                      JoinOption = attr.ib()
    join_table:                str =        attr.ib()


def create_relationship(
        target_entity_class_name: str,
        nullable:                 bool,
        lazy:                     bool,
        join:                     JoinOption,
        join_table:               Optional[str] = None,
        property_name:            Optional[str] = None,
) -> Relationship:
    target_entity_python_name = pythonize(target_entity_class_name)
    return Relationship(
        python_name=target_entity_python_name,
        target_entity_class_name=target_entity_class_name,
        target_entity_python_name=target_entity_python_name,
        property_name=property_name if property_name else target_entity_python_name,
        nullable=nullable,
        lazy=lazy,
        join=join,
        join_table=str(join_table) if join_table else None,
    )
