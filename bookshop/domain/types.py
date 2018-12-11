from typing import Mapping, List

from sqlalchemy.ext.declarative import DeclarativeMeta

import attr


class UserJson(dict):
    """Used to represent JSON provided by the user, which should
    not have its contents modified during serialization"""
    ...


@attr.s(frozen=True, auto_attribs=True)
class Relationship:
    sqlalchemy_model_class:    DeclarativeMeta
    target_name:               str
    target_identifier_column:  str
    source_foreign_key_column: str
    lazy:                      bool
    nullable:                  bool


@attr.s(frozen=True, auto_attribs=True)
class DomainModel:
    external_identifier_map: Mapping[str, Relationship]
    identifier_column_name:  str
    relationship_keys:       List[str]
    property_keys:           List[str]
    json_translation_map:    Mapping[str, str]
    eager_relationships:     List[str]
