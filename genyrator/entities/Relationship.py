from enum import Enum
from typing import Optional
import attr
from genyrator.inflector import pythonize, to_json_case, to_class_name


class JoinOption(Enum):
    to_one =  'to_one'
    to_many = 'to_many'


@attr.s
class Relationship(object):
    python_name:                    str =           attr.ib()
    target_entity_class_name:       str =           attr.ib()
    target_entity_python_name:      str =           attr.ib()
    target_foreign_key_column_name: Optional[str] = attr.ib()
    source_foreign_key_column_name: Optional[str] = attr.ib()
    source_identifier_column_name:  str =           attr.ib()
    property_name:                  str =           attr.ib()
    json_property_name:             str =           attr.ib()
    # in the json request, what key will this appear under?
    key_alias_in_json:              str =           attr.ib()
    nullable:                       bool =          attr.ib()
    lazy:                           bool =          attr.ib()
    join:                           JoinOption =    attr.ib()
    secondary_join_name:            Optional[str] = attr.ib()


@attr.s
class RelationshipWithoutJoinTable(Relationship):
    target_identifier_column_name: str = attr.ib()


@attr.s
class RelationshipWithJoinTable(Relationship):
    join_table:            str = attr.ib()
    join_table_class_name: str = attr.ib()


def create_relationship(
        target_entity_class_name:       str,
        nullable:                       bool,
        lazy:                           bool,
        join:                           JoinOption,
        source_identifier_column_name:  str,
        *,
        source_foreign_key_column_name: Optional[str] = None,
        key_alias_in_json:              Optional[str] = None,
        join_table:                     Optional[str] = None,
        target_identifier_column_name:  Optional[str] = None,
        target_foreign_key_column_name: Optional[str] = None,
        property_name:                  Optional[str] = None,
        secondary_join_name:            Optional[str] = None,
) -> Relationship:
    """Return a relationship between two entities

    Args:
        target_entity_class_name:  The entity this relationship is pointing to
                                   (ie. not the entity it is defined on).

        nullable: Early validation for whether the target column is nullable.

        lazy: If False the target entity is embedded in the JSON response.

        join: Whether the relationship is 1-to-1 or 1-to-many. If 1-to-1 the property
              will be scalar, if 1-to-many it will be a list.

        source_identifier_column_name: The identifier column for the entity
                                       this relationship starts from. This is
                                       *not* the join key.

        source_foreign_key_column_name: The foreign key property on the entity
                                        this relationship starts from. This will
                                        be None for 1-to-many relationship.

        key_alias_in_json: The name used for this relationship when it appears in JSON.
                           This needs to be unique for a model.
                           Has sensible default.

        join_table: The table name to join through to the target entity.
                    This is usually only needed for many-to-many relationships.

        target_identifier_column_name: The identifier column of the target entity. (deprecated)

        target_foreign_key_column_name: The column name of the foreign key on the
                                        target model. This is usually only needed if
                                        there are multiple routes to the other entity.

        property_name: The property name used on the SQLAlchemy model.

        secondary_join_name: The column name of the secondary foreign key on the
                             intermediary join table when doing a many-to-many join
                             on a self-referential many-to-many relationship.
                             See: https://docs.sqlalchemy.org/en/latest/orm/join_conditions.html#self-referential-many-to-many-relationship
    """
    if source_foreign_key_column_name is not None:
        if target_foreign_key_column_name is not None:
            raise Exception('Cannot provide both source and target foreign key columns')
        if join != JoinOption.to_one:
            raise Exception('Can only provide source foreign key column on to-one relationships')

    target_entity_python_name = pythonize(target_entity_class_name)
    property_name = property_name if property_name is not None else target_entity_python_name

    if key_alias_in_json is None:
        if target_identifier_column_name is None:
            raise Exception('Must have a key_alias_in_json or target_idenfitier_column_name')
        key_alias_in_json = target_identifier_column_name

    relationship = Relationship(
        python_name=target_entity_python_name,
        target_entity_class_name=target_entity_class_name,
        target_entity_python_name=target_entity_python_name,
        target_foreign_key_column_name=target_foreign_key_column_name,
        source_identifier_column_name=source_identifier_column_name,
        source_foreign_key_column_name=source_foreign_key_column_name,
        property_name=property_name,
        json_property_name=to_json_case(property_name),
        key_alias_in_json=key_alias_in_json,
        nullable=nullable,
        lazy=lazy,
        join=join,
        secondary_join_name=secondary_join_name,
    )
    if join_table is None:
        properties = relationship.__dict__
        properties.update({
            'target_identifier_column_name': pythonize(target_identifier_column_name) if target_identifier_column_name else None,
        })
        return RelationshipWithoutJoinTable(**properties)
    else:
        properties = relationship.__dict__
        properties.update({
            'join_table': join_table,
            'join_table_class_name': to_class_name(join_table),
        })
        return RelationshipWithJoinTable(**properties)
